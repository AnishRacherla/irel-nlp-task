"""
Prerequisite mapping module
Maps prerequisite relationships between concepts based on pedagogical flow
"""

from typing import Dict, List, Any, Tuple
import openai
import json
from collections import defaultdict


class PrerequisiteMapper:
    """Map prerequisite relationships between educational concepts"""
    
    def __init__(self, config: Dict[str, Any], logger):
        """
        Initialize prerequisite mapper
        
        Args:
            config: Configuration dictionary
            logger: Logger instance
        """
        self.config = config
        self.logger = logger
        self.openai_api_key = config.get('api_keys', {}).get('openai_api_key', '')
        
        if self.openai_api_key:
            openai.api_key = self.openai_api_key
    
    def map_prerequisites(self, transcript: str, concepts: List[Dict[str, Any]], 
                         domain: str = "Computer Science") -> Dict[str, Any]:
        """
        Map prerequisite relationships between concepts
        
        Args:
            transcript: Educational transcript
            concepts: List of extracted concepts
            domain: Academic domain
        
        Returns:
            Dictionary containing prerequisite relationships
        """
        try:
            self.logger.info("Mapping prerequisite relationships using LLM")
            
            # Prepare concepts list for the prompt
            concepts_text = "\n".join([
                f"{i+1}. {c['name']} (ID: {c['id']}): {c['description']}"
                for i, c in enumerate(concepts)
            ])
            
            prompt = f"""You are an expert in {domain} pedagogy and curriculum design. Analyze the following educational transcript and the extracted concepts to determine the prerequisite relationships.

A prerequisite relationship means: Concept A must be understood before Concept B can be effectively learned.

Transcript excerpt (focus on the pedagogical flow):
{transcript[:3000]}...

Extracted Concepts:
{concepts_text}

Your task:
1. Identify which concepts are prerequisites for others based on the teaching flow
2. Determine the strength of each prerequisite relationship (0.0 to 1.0)
3. Classify relationship types:
   - "strict_prerequisite": A must be learned before B
   - "recommended_prerequisite": A helps understand B but isn't strictly required
   - "related": A and B are related but no clear prerequisite order
   - "builds_on": B extends or builds upon A

Respond in the following JSON format:
{{
    "relationships": [
        {{
            "source_id": "concept_1",
            "source_name": "Concept A",
            "target_id": "concept_2",
            "target_name": "Concept B",
            "relationship_type": "strict_prerequisite",
            "confidence": 0.9,
            "reasoning": "Brief explanation of why this relationship exists"
        }}
    ],
    "concept_order": ["concept_1", "concept_2", ...],
    "learning_paths": [
        {{
            "path_name": "Core Path",
            "concepts": ["concept_1", "concept_2", "concept_3"],
            "description": "Main learning sequence"
        }}
    ]
}}

Only include relationships where you have reasonable confidence (>0.5).
"""
            
            client = openai.OpenAI(api_key=self.openai_api_key)
            response = client.chat.completions.create(
                model=self.config.get('concept_extraction', {}).get('model', 'gpt-4o-mini'),
                messages=[
                    {"role": "system", "content": "You are an expert in educational content analysis and curriculum design. Always respond with valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                response_format={"type": "json_object"}
            )
            
            result = response.choices[0].message.content
            relationships_dict = json.loads(result)
            
            self.logger.info(f"Mapped {len(relationships_dict.get('relationships', []))} prerequisite relationships")
            
            return relationships_dict
            
        except Exception as e:
            self.logger.error(f"Error in prerequisite mapping: {str(e)}")
            return {
                'relationships': [],
                'concept_order': [c['id'] for c in concepts],
                'learning_paths': []
            }
    
    def filter_relationships(self, relationships: List[Dict[str, Any]], 
                           min_confidence: float = 0.6) -> List[Dict[str, Any]]:
        """
        Filter relationships by confidence threshold
        
        Args:
            relationships: List of relationships
            min_confidence: Minimum confidence threshold
        
        Returns:
            Filtered relationships
        """
        filtered = [r for r in relationships if r.get('confidence', 0) >= min_confidence]
        
        if len(filtered) < len(relationships):
            self.logger.info(f"Filtered {len(relationships) - len(filtered)} low-confidence relationships")
        
        return filtered
    
    def build_dependency_graph(self, concepts: List[Dict[str, Any]], 
                              relationships: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Build a dependency graph structure
        
        Args:
            concepts: List of concepts
            relationships: List of relationships
        
        Returns:
            Graph structure
        """
        # Create nodes
        nodes = {}
        for concept in concepts:
            nodes[concept['id']] = {
                'id': concept['id'],
                'name': concept['name'],
                'description': concept.get('description', ''),
                'importance': concept.get('importance', 3),
                'prerequisites': [],
                'dependents': []
            }
        
        # Add edges
        for rel in relationships:
            source_id = rel.get('source_id')
            target_id = rel.get('target_id')
            
            if source_id in nodes and target_id in nodes:
                # source is prerequisite for target
                nodes[target_id]['prerequisites'].append({
                    'concept_id': source_id,
                    'type': rel.get('relationship_type'),
                    'confidence': rel.get('confidence')
                })
                
                # target depends on source
                nodes[source_id]['dependents'].append({
                    'concept_id': target_id,
                    'type': rel.get('relationship_type'),
                    'confidence': rel.get('confidence')
                })
        
        return {
            'nodes': list(nodes.values()),
            'edges': relationships,
            'node_count': len(nodes),
            'edge_count': len(relationships)
        }
    
    def identify_foundational_concepts(self, graph: Dict[str, Any]) -> List[str]:
        """
        Identify foundational concepts (those with no prerequisites)
        
        Args:
            graph: Dependency graph
        
        Returns:
            List of foundational concept IDs
        """
        foundational = []
        for node in graph['nodes']:
            if len(node['prerequisites']) == 0:
                foundational.append(node['id'])
        
        self.logger.info(f"Identified {len(foundational)} foundational concepts")
        return foundational
    
    def map_and_build(self, transcript: str, concepts: List[Dict[str, Any]], 
                     domain: str = "Computer Science") -> Dict[str, Any]:
        """
        Complete prerequisite mapping pipeline
        
        Args:
            transcript: Educational transcript
            concepts: List of concepts
            domain: Academic domain
        
        Returns:
            Complete prerequisite map with graph structure
        """
        # Map relationships
        mapping_result = self.map_prerequisites(transcript, concepts, domain)
        
        # Filter relationships
        min_confidence = self.config.get('prerequisite_mapping', {}).get('confidence_threshold', 0.6)
        relationships = self.filter_relationships(
            mapping_result.get('relationships', []),
            min_confidence
        )
        
        # Build graph
        graph = self.build_dependency_graph(concepts, relationships)
        
        # Identify foundational concepts
        foundational = self.identify_foundational_concepts(graph)
        
        # Combine results
        return {
            'relationships': relationships,
            'concept_order': mapping_result.get('concept_order', []),
            'learning_paths': mapping_result.get('learning_paths', []),
            'dependency_graph': graph,
            'foundational_concepts': foundational,
            'statistics': {
                'total_concepts': len(concepts),
                'total_relationships': len(relationships),
                'foundational_count': len(foundational),
                'avg_prerequisites': sum(len(n['prerequisites']) for n in graph['nodes']) / len(graph['nodes']) if graph['nodes'] else 0
            }
        }
