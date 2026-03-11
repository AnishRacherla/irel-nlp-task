"""
Concept extraction module
Extracts educational concepts from processed transcripts
"""

from typing import Dict, List, Any
import openai
import json


class ConceptExtractor:
    """Extract technical concepts from educational content"""
    
    def __init__(self, config: Dict[str, Any], logger):
        """
        Initialize concept extractor
        
        Args:
            config: Configuration dictionary
            logger: Logger instance
        """
        self.config = config
        self.logger = logger
        self.openai_api_key = config.get('api_keys', {}).get('openai_api_key', '')
        
        if self.openai_api_key:
            openai.api_key = self.openai_api_key
    
    def extract_concepts(self, text: str, domain: str = "Computer Science") -> Dict[str, Any]:
        """
        Extract core technical concepts from educational content
        
        Args:
            text: Input text (preferably standardized)
            domain: Academic domain
        
        Returns:
            Dictionary containing extracted concepts with metadata
        """
        try:
            self.logger.info("Extracting concepts using LLM")
            
            prompt = f"""You are an expert in {domain} education and curriculum design. Analyze the following educational transcript and extract the core technical concepts being taught.

For each concept, provide:
1. Concept name (concise, standardized terminology)
2. Description (brief explanation of the concept)
3. Importance level (1-5, where 5 is most fundamental/important)
4. Keywords/aliases (alternative terms or related keywords)
5. Time range (approximate when in the lesson this concept appears - early, middle, late)

Transcript:
{text}

Respond in the following JSON format:
{{
    "concepts": [
        {{
            "id": "concept_1",
            "name": "Concept Name",
            "description": "Brief description",
            "importance": 4,
            "keywords": ["keyword1", "keyword2"],
            "time_segment": "early|middle|late",
            "category": "fundamental|intermediate|advanced"
        }}
    ],
    "total_concepts": 0,
    "domain": "{domain}",
    "main_topic": "Overall topic of the lesson"
}}

Extract 5-20 concepts depending on the content complexity. Focus on the most important and clearly taught concepts.
"""
            
            client = openai.OpenAI(api_key=self.openai_api_key)
            response = client.chat.completions.create(
                model=self.config.get('concept_extraction', {}).get('model', 'gpt-4o-mini'),
                messages=[
                    {"role": "system", "content": "You are an expert in educational content analysis and concept extraction. Always respond with valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                response_format={"type": "json_object"}
            )
            
            result = response.choices[0].message.content
            concepts_dict = json.loads(result)
            
            # Update total_concepts
            concepts_dict['total_concepts'] = len(concepts_dict.get('concepts', []))
            
            self.logger.info(f"Extracted {concepts_dict['total_concepts']} concepts")
            
            return concepts_dict
            
        except Exception as e:
            self.logger.error(f"Error in concept extraction: {str(e)}")
            return {
                'concepts': [],
                'total_concepts': 0,
                'domain': domain,
                'main_topic': 'Unknown'
            }
    
    def refine_concepts(self, concepts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Refine and deduplicate extracted concepts
        
        Args:
            concepts: List of extracted concepts
        
        Returns:
            Refined list of concepts
        """
        # Simple deduplication based on name similarity
        unique_concepts = []
        seen_names = set()
        
        for concept in concepts:
            name_lower = concept['name'].lower()
            
            # Check if similar concept already exists
            is_duplicate = False
            for seen in seen_names:
                # Simple similarity check
                if name_lower in seen or seen in name_lower:
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                unique_concepts.append(concept)
                seen_names.add(name_lower)
        
        if len(unique_concepts) < len(concepts):
            self.logger.info(f"Removed {len(concepts) - len(unique_concepts)} duplicate concepts")
        
        return unique_concepts
    
    def categorize_concepts(self, concepts: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """
        Categorize concepts by type or level
        
        Args:
            concepts: List of concepts
        
        Returns:
            Dictionary with categorized concepts
        """
        categorized = {
            'fundamental': [],
            'intermediate': [],
            'advanced': []
        }
        
        for concept in concepts:
            category = concept.get('category', 'intermediate')
            if category in categorized:
                categorized[category].append(concept)
        
        return categorized
    
    def extract_and_refine(self, text: str, domain: str = "Computer Science") -> Dict[str, Any]:
        """
        Complete extraction pipeline with refinement
        
        Args:
            text: Input text
            domain: Academic domain
        
        Returns:
            Refined concept extraction results
        """
        # Extract concepts
        extraction_result = self.extract_concepts(text, domain)
        
        # Refine concepts
        concepts = extraction_result.get('concepts', [])
        refined_concepts = self.refine_concepts(concepts)
        
        # Categorize
        categorized = self.categorize_concepts(refined_concepts)
        
        # Update result
        extraction_result['concepts'] = refined_concepts
        extraction_result['total_concepts'] = len(refined_concepts)
        extraction_result['categorized'] = categorized
        
        return extraction_result
