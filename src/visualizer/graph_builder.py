"""
Visualization module for concept dependency graphs
"""

from typing import Dict, Any, List
import json
import numpy as np
import networkx as nx
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from pyvis.network import Network


class GraphVisualizer:
    """Visualize concept dependency graphs"""
    
    def __init__(self, config: Dict[str, Any], logger):
        """
        Initialize graph visualizer
        
        Args:
            config: Configuration dictionary
            logger: Logger instance
        """
        self.config = config
        self.logger = logger
        
        # Get output paths
        self.graphs_dir = Path(config.get('paths', {}).get('graphs_dir', 'outputs/graphs'))
        self.viz_dir = Path(config.get('paths', {}).get('visualizations_dir', 'outputs/visualizations'))
        
        # Ensure directories exist
        self.graphs_dir.mkdir(parents=True, exist_ok=True)
        self.viz_dir.mkdir(parents=True, exist_ok=True)
    
    def convert_numpy_types(self, obj):
        """
        Recursively convert numpy types to Python native types for JSON serialization
        
        Args:
            obj: Object that may contain numpy types
        
        Returns:
            Object with numpy types converted to Python types
        """
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, dict):
            return {key: self.convert_numpy_types(value) for key, value in obj.items()}
        elif isinstance(obj, list):
            return [self.convert_numpy_types(item) for item in obj]
        else:
            return obj
    
    def save_json(self, data: Dict[str, Any], video_id: str, filename: str = "concept_graph.json"):
        """
        Save graph data as JSON
        
        Args:
            data: Graph data dictionary
            video_id: Video identifier
            filename: Output filename
        """
        output_path = self.graphs_dir / f"{video_id}_{filename}"
        
        # Convert numpy types to Python native types
        data_clean = self.convert_numpy_types(data)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data_clean, f, ensure_ascii=False, indent=2)
        
        self.logger.info(f"Saved JSON graph: {output_path}")
        return output_path
    
    def build_networkx_graph(self, graph_data: Dict[str, Any]) -> nx.DiGraph:
        """
        Build NetworkX directed graph from graph data
        
        Args:
            graph_data: Graph data with nodes and edges
        
        Returns:
            NetworkX DiGraph
        """
        G = nx.DiGraph()
        
        # Add nodes
        for node in graph_data.get('nodes', []):
            G.add_node(
                node['id'],
                name=node['name'],
                description=node.get('description', ''),
                importance=node.get('importance', 3)
            )
        
        # Add edges
        for edge in graph_data.get('edges', []):
            G.add_edge(
                edge['source_id'],
                edge['target_id'],
                type=edge.get('relationship_type', 'prerequisite'),
                confidence=edge.get('confidence', 0.5),
                reasoning=edge.get('reasoning', '')
            )
        
        return G
    
    def save_graphml(self, graph_data: Dict[str, Any], video_id: str):
        """
        Save graph in GraphML format
        
        Args:
            graph_data: Graph data
            video_id: Video identifier
        """
        G = self.build_networkx_graph(graph_data)
        output_path = self.graphs_dir / f"{video_id}_graph.graphml"
        
        nx.write_graphml(G, output_path)
        self.logger.info(f"Saved GraphML: {output_path}")
        return output_path
    
    def save_dot(self, graph_data: Dict[str, Any], video_id: str):
        """
        Save graph in DOT format (GraphViz)
        
        Args:
            graph_data: Graph data
            video_id: Video identifier
        """
        G = self.build_networkx_graph(graph_data)
        output_path = self.graphs_dir / f"{video_id}_graph.dot"
        
        nx.drawing.nx_pydot.write_dot(G, output_path)
        self.logger.info(f"Saved DOT file: {output_path}")
        return output_path
    
    def create_static_visualization(self, graph_data: Dict[str, Any], video_id: str, 
                                   title: str = "Concept Dependency Graph"):
        """
        Create static matplotlib visualization
        
        Args:
            graph_data: Graph data
            video_id: Video identifier
            title: Graph title
        """
        try:
            G = self.build_networkx_graph(graph_data)
            
            # Create figure
            plt.figure(figsize=(16, 12))
            
            # Use hierarchical layout
            try:
                pos = nx.spring_layout(G, k=2, iterations=50, seed=42)
            except:
                pos = nx.spring_layout(G, seed=42)
            
            # Node colors based on importance
            node_colors = []
            for node_id in G.nodes():
                importance = G.nodes[node_id].get('importance', 3)
                if importance >= 4:
                    node_colors.append('#FF6B6B')  # High importance - red
                elif importance >= 3:
                    node_colors.append('#4ECDC4')  # Medium importance - teal
                else:
                    node_colors.append('#95E1D3')  # Low importance - light green
            
            # Draw nodes
            nx.draw_networkx_nodes(G, pos, node_color=node_colors, 
                                 node_size=3000, alpha=0.9, linewidths=2, 
                                 edgecolors='black')
            
            # Draw edges with different styles
            edge_colors = []
            edge_styles = []
            for edge in G.edges(data=True):
                rel_type = edge[2].get('type', 'prerequisite')
                if rel_type == 'strict_prerequisite':
                    edge_colors.append('#2C3E50')
                    edge_styles.append('solid')
                elif rel_type == 'recommended_prerequisite':
                    edge_colors.append('#34495E')
                    edge_styles.append('dashed')
                else:
                    edge_colors.append('#7F8C8D')
                    edge_styles.append('dotted')
            
            nx.draw_networkx_edges(G, pos, edge_color=edge_colors, 
                                 style=edge_styles, arrows=True, 
                                 arrowsize=20, width=2, alpha=0.6,
                                 connectionstyle='arc3,rad=0.1')
            
            # Draw labels
            labels = {node_id: G.nodes[node_id]['name'] for node_id in G.nodes()}
            nx.draw_networkx_labels(G, pos, labels, font_size=9, 
                                   font_weight='bold', font_family='sans-serif')
            
            # Add legend
            high_patch = mpatches.Patch(color='#FF6B6B', label='High Importance')
            med_patch = mpatches.Patch(color='#4ECDC4', label='Medium Importance')
            low_patch = mpatches.Patch(color='#95E1D3', label='Low Importance')
            plt.legend(handles=[high_patch, med_patch, low_patch], loc='upper left')
            
            plt.title(title, fontsize=16, fontweight='bold', pad=20)
            plt.axis('off')
            plt.tight_layout()
            
            # Save
            output_path = self.viz_dir / f"{video_id}_graph.png"
            plt.savefig(output_path, dpi=300, bbox_inches='tight', 
                       facecolor='white', edgecolor='none')
            plt.close()
            
            self.logger.info(f"Saved static visualization: {output_path}")
            return output_path
            
        except Exception as e:
            self.logger.error(f"Error creating static visualization: {str(e)}")
            return None
    
    def create_interactive_visualization(self, graph_data: Dict[str, Any], video_id: str,
                                       title: str = "Interactive Concept Dependency Graph"):
        """
        Create interactive HTML visualization using pyvis
        
        Args:
            graph_data: Graph data
            video_id: Video identifier
            title: Graph title
        """
        try:
            # Create pyvis network
            net = Network(height='800px', width='100%', directed=True, 
                         bgcolor='#ffffff', font_color='black')
            
            # Configure physics
            net.set_options("""
            {
                "physics": {
                    "enabled": true,
                    "barnesHut": {
                        "gravitationalConstant": -8000,
                        "centralGravity": 0.3,
                        "springLength": 200,
                        "springConstant": 0.04
                    }
                },
                "edges": {
                    "smooth": {
                        "type": "curvedCW",
                        "roundness": 0.2
                    }
                }
            }
            """)
            
            # Add nodes
            for node in graph_data.get('nodes', []):
                importance = node.get('importance', 3)
                
                # Color based on importance
                if importance >= 4:
                    color = '#FF6B6B'
                elif importance >= 3:
                    color = '#4ECDC4'
                else:
                    color = '#95E1D3'
                
                # Node size based on importance
                size = 20 + (importance * 5)
                
                # Add node
                net.add_node(
                    node['id'],
                    label=node['name'],
                    title=f"<b>{node['name']}</b><br>{node.get('description', '')}",
                    color=color,
                    size=size,
                    borderWidth=2
                )
            
            # Add edges
            for edge in graph_data.get('edges', []):
                rel_type = edge.get('relationship_type', 'prerequisite')
                confidence = edge.get('confidence', 0.5)
                
                # Edge color and style based on type
                if rel_type == 'strict_prerequisite':
                    color = '#2C3E50'
                    width = 3
                    dashes = False
                elif rel_type == 'recommended_prerequisite':
                    color = '#34495E'
                    width = 2
                    dashes = [5, 5]
                else:
                    color = '#7F8C8D'
                    width = 1
                    dashes = [2, 2]
                
                title = f"{rel_type}<br>Confidence: {confidence:.2f}<br>{edge.get('reasoning', '')}"
                
                net.add_edge(
                    edge['source_id'],
                    edge['target_id'],
                    title=title,
                    color=color,
                    width=width,
                    dashes=dashes
                )
            
            # Save
            output_path = self.viz_dir / f"{video_id}_interactive_graph.html"
            net.save_graph(str(output_path))
            
            self.logger.info(f"Saved interactive visualization: {output_path}")
            return output_path
            
        except Exception as e:
            self.logger.error(f"Error creating interactive visualization: {str(e)}")
            return None
    
    def generate_all_outputs(self, prerequisite_data: Dict[str, Any], video_id: str, 
                           title: str = "Concept Dependency Graph") -> Dict[str, Path]:
        """
        Generate all output formats
        
        Args:
            prerequisite_data: Complete prerequisite mapping data
            video_id: Video identifier
            title: Graph title
        
        Returns:
            Dictionary of output paths
        """
        self.logger.info(f"Generating all outputs for {video_id}")
        
        outputs = {}
        
        # Convert concepts/relationships to dependency_graph format if needed
        if 'dependency_graph' not in prerequisite_data and 'concepts' in prerequisite_data:
            graph_data = {
                'nodes': [
                    {
                        'id': c['id'],
                        'name': c['name'],
                        'description': c.get('description', ''),
                        'importance': c.get('importance', 1)
                    }
                    for c in prerequisite_data.get('concepts', [])
                ],
                'edges': [
                    {
                        'source_id': r.get('source'),
                        'target_id': r.get('target'),
                        'confidence': r.get('confidence', 0.5),
                        'relationship_type': r.get('strength', 'prerequisite'),
                        'reasoning': f"Confidence: {r.get('confidence', 0.5):.2f}"
                    }
                    for r in prerequisite_data.get('relationships', [])
                ]
            }
        else:
            graph_data = prerequisite_data.get('dependency_graph', {})
        
        # JSON
        outputs['json'] = self.save_json(prerequisite_data, video_id, "complete_output.json")
        outputs['graph_json'] = self.save_json(graph_data, video_id, "graph.json")
        
        # GraphML
        try:
            outputs['graphml'] = self.save_graphml(graph_data, video_id)
        except Exception as e:
            self.logger.warning(f"Could not save GraphML: {str(e)}")
        
        # DOT
        try:
            outputs['dot'] = self.save_dot(graph_data, video_id)
        except Exception as e:
            self.logger.warning(f"Could not save DOT: {str(e)}")
        
        # Static visualization
        outputs['static_viz'] = self.create_static_visualization(graph_data, video_id, title)
        
        # Interactive visualization
        outputs['interactive_viz'] = self.create_interactive_visualization(graph_data, video_id, title)
        
        self.logger.info(f"Generated {len(outputs)} output files")
        return outputs
