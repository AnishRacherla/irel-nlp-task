"""
Visualization module for concept dependency graphs
"""

from typing import Dict, Any, List
from collections import defaultdict
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
                label=node['name'],
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
    
    def _hierarchical_layout(self, G: nx.DiGraph) -> dict:
        """
        Compute a top-to-bottom hierarchical layout based on topological sort.
        Nodes with no predecessors (foundational concepts) are at the top;
        nodes with no successors (advanced concepts) are at the bottom.
        
        Returns:
            pos dict mapping node_id -> (x, y)
        """
        # Assign each node to a layer via longest-path from sources
        if len(G.nodes) == 0:
            return {}
        
        try:
            layers: Dict[str, int] = {}
            # BFS/DFS from roots to assign layers
            roots = [n for n in G.nodes() if G.in_degree(n) == 0]
            if not roots:
                # Fallback: break a cycle by picking the node with highest out-degree
                roots = [max(G.nodes(), key=lambda n: G.out_degree(n))]
            
            queue = list(roots)
            for r in roots:
                layers[r] = 0
            
            visited = set(roots)
            while queue:
                current = queue.pop(0)
                for successor in G.successors(current):
                    new_layer = layers[current] + 1
                    if successor not in layers or layers[successor] < new_layer:
                        layers[successor] = new_layer
                    if successor not in visited:
                        visited.add(successor)
                        queue.append(successor)
            
            # Any unvisited node (disconnected) gets layer 0
            for n in G.nodes():
                if n not in layers:
                    layers[n] = 0
            
            # Group nodes by layer
            layer_nodes: Dict[int, list] = defaultdict(list)
            for node, layer in layers.items():
                layer_nodes[layer].append(node)
            
            max_layer = max(layer_nodes.keys()) if layer_nodes else 0
            
            pos = {}
            for layer, nodes_in_layer in layer_nodes.items():
                n = len(nodes_in_layer)
                for i, node in enumerate(nodes_in_layer):
                    x = (i - (n - 1) / 2.0) * 2.5
                    y = -(layer / max(max_layer, 1)) * 6  # invert so top=0
                    pos[node] = (x, y)
            
            return pos
        except Exception:
            return nx.spring_layout(G, seed=42)

    def create_static_visualization(self, graph_data: Dict[str, Any], video_id: str, 
                                   title: str = "Concept Dependency Graph"):
        """
        Create static matplotlib visualization with hierarchical directed layout.
        Arrows point FROM prerequisite TO dependent concept (top → bottom).
        """
        try:
            G = self.build_networkx_graph(graph_data)
            
            if len(G.nodes) == 0:
                self.logger.warning("No nodes to visualize")
                return None

            fig, ax = plt.subplots(figsize=(18, 13))
            
            # Hierarchical layout: prerequisites on top, dependents below
            pos = self._hierarchical_layout(G)

            # Node colors based on importance
            node_colors = []
            node_sizes = []
            for node_id in G.nodes():
                importance = G.nodes[node_id].get('importance', 3)
                if importance >= 4:
                    node_colors.append('#E74C3C')   # High importance - red
                    node_sizes.append(3500)
                elif importance >= 3:
                    node_colors.append('#3498DB')   # Medium importance - blue
                    node_sizes.append(2800)
                else:
                    node_colors.append('#2ECC71')   # Low importance - green
                    node_sizes.append(2200)

            # Separate edges by type for individual drawing
            strict_edges = [(u, v) for u, v, d in G.edges(data=True)
                            if d.get('type') == 'strict_prerequisite']
            recommended_edges = [(u, v) for u, v, d in G.edges(data=True)
                                 if d.get('type') == 'recommended_prerequisite']
            related_edges = [(u, v) for u, v, d in G.edges(data=True)
                             if d.get('type') not in ('strict_prerequisite', 'recommended_prerequisite')]

            common_edge_kw = dict(ax=ax, arrows=True, arrowsize=25, width=2.5,
                                  connectionstyle='arc3,rad=0.08',
                                  node_size=node_sizes)

            if strict_edges:
                nx.draw_networkx_edges(G, pos, edgelist=strict_edges,
                                       edge_color='#2C3E50', style='solid',
                                       alpha=0.85, **common_edge_kw)
            if recommended_edges:
                nx.draw_networkx_edges(G, pos, edgelist=recommended_edges,
                                       edge_color='#8E44AD', style='dashed',
                                       alpha=0.75, **common_edge_kw)
            if related_edges:
                nx.draw_networkx_edges(G, pos, edgelist=related_edges,
                                       edge_color='#95A5A6', style='dotted',
                                       alpha=0.6, **common_edge_kw)

            # Draw nodes on top of edges
            nx.draw_networkx_nodes(G, pos, node_color=node_colors,
                                   node_size=node_sizes, alpha=0.95,
                                   linewidths=2, edgecolors='#2C3E50', ax=ax)

            # Draw wrapped labels
            labels = {}
            for node_id in G.nodes():
                name = G.nodes[node_id]['name']
                # Wrap long names onto two lines
                words = name.split()
                if len(words) > 3:
                    mid = len(words) // 2
                    name = ' '.join(words[:mid]) + '\n' + ' '.join(words[mid:])
                labels[node_id] = name
            nx.draw_networkx_labels(G, pos, labels, font_size=8,
                                    font_weight='bold', ax=ax)

            # Legend
            high_patch = mpatches.Patch(color='#E74C3C', label='High Importance')
            med_patch  = mpatches.Patch(color='#3498DB', label='Medium Importance')
            low_patch  = mpatches.Patch(color='#2ECC71', label='Low Importance')
            strict_line      = mpatches.Patch(color='#2C3E50', label='Strict Prerequisite  →')
            recommended_line = mpatches.Patch(color='#8E44AD', label='Recommended Prerequisite  →')
            related_line     = mpatches.Patch(color='#95A5A6', label='Related  →')
            ax.legend(handles=[high_patch, med_patch, low_patch,
                                strict_line, recommended_line, related_line],
                      loc='upper left', fontsize=9, framealpha=0.9)

            ax.set_title(f"{title}\n(Arrow direction: prerequisite  →  dependent concept)",
                         fontsize=14, fontweight='bold', pad=16)
            ax.axis('off')
            fig.tight_layout()

            output_path = self.viz_dir / f"{video_id}_graph.png"
            fig.savefig(output_path, dpi=300, bbox_inches='tight',
                        facecolor='white', edgecolor='none')
            plt.close(fig)

            self.logger.info(f"Saved static visualization: {output_path}")
            return output_path

        except Exception as e:
            self.logger.error(f"Error creating static visualization: {str(e)}")
            return None
    
    def create_interactive_visualization(self, graph_data: Dict[str, Any], video_id: str,
                                       title: str = "Interactive Concept Dependency Graph"):
        """
        Create interactive HTML visualization using pyvis.
        Uses a hierarchical top-to-bottom layout so that prerequisite concepts
        appear above the concepts they unlock.  Arrow tip always points TO the
        dependent concept (prerequisite → dependent).
        """
        try:
            # Build a NetworkX graph first so we can compute hierarchical levels
            G_nx = self.build_networkx_graph(graph_data)
            hier_pos = self._hierarchical_layout(G_nx)

            # Map node id → (x, y) scaled for pyvis pixel coordinates
            # pyvis uses pixels; scale the unit coords to ~800px wide and ~600px tall
            x_vals = [p[0] for p in hier_pos.values()] if hier_pos else [0]
            y_vals = [p[1] for p in hier_pos.values()] if hier_pos else [0]
            x_range = max(abs(max(x_vals)), abs(min(x_vals)), 1)
            y_range = max(abs(max(y_vals)), abs(min(y_vals)), 1)

            def to_px(node_id):
                x, y = hier_pos.get(node_id, (0, 0))
                return (x / x_range) * 600, (y / y_range) * 400

            # Create pyvis network with hierarchical layout disabled in physics
            # (we pin node positions manually)
            net = Network(height='850px', width='100%', directed=True,
                          bgcolor='#f8f9fa', font_color='#2C3E50')

            net.set_options("""
            {
                "physics": {
                    "enabled": false
                },
                "layout": {
                    "hierarchical": {
                        "enabled": true,
                        "direction": "UD",
                        "sortMethod": "directed",
                        "levelSeparation": 160,
                        "nodeSpacing": 200,
                        "treeSpacing": 250
                    }
                },
                "edges": {
                    "arrows": {
                        "to": {
                            "enabled": true,
                            "scaleFactor": 1.4
                        }
                    },
                    "smooth": {
                        "enabled": true,
                        "type": "cubicBezier",
                        "forceDirection": "vertical",
                        "roundness": 0.4
                    },
                    "color": {
                        "inherit": false
                    },
                    "font": {
                        "size": 11,
                        "align": "middle"
                    }
                },
                "nodes": {
                    "shape": "box",
                    "margin": 10,
                    "widthConstraint": { "maximum": 180 },
                    "font": { "size": 13, "bold": true },
                    "shadow": { "enabled": true, "size": 5, "x": 3, "y": 3 }
                },
                "interaction": {
                    "hover": true,
                    "tooltipDelay": 100,
                    "navigationButtons": true,
                    "keyboard": true
                }
            }
            """)

            # Add nodes
            for node in graph_data.get('nodes', []):
                importance = node.get('importance', 3)
                node_id = node['id']

                if importance >= 4:
                    bg_color  = '#E74C3C'
                    txt_color = '#ffffff'
                    border    = '#922B21'
                elif importance >= 3:
                    bg_color  = '#2980B9'
                    txt_color = '#ffffff'
                    border    = '#1A5276'
                else:
                    bg_color  = '#27AE60'
                    txt_color = '#ffffff'
                    border    = '#1E8449'

                # Compute predecessor count for tooltip
                prereq_count = G_nx.in_degree(node_id) if node_id in G_nx else 0
                dep_count    = G_nx.out_degree(node_id) if node_id in G_nx else 0

                tooltip = (
                    f"<b>{node['name']}</b><br>"
                    f"{node.get('description', '')}<br><br>"
                    f"<i>Importance: {importance}/5</i><br>"
                    f"Prerequisites: {prereq_count} concept(s)<br>"
                    f"Unlocks: {dep_count} concept(s)"
                )

                net.add_node(
                    node_id,
                    label=node['name'],
                    title=tooltip,
                    color={'background': bg_color, 'border': border,
                           'highlight': {'background': '#F39C12', 'border': '#D35400'}},
                    font={'color': txt_color, 'size': 13},
                    size=22 + (importance * 4),
                    borderWidth=2,
                    level=None   # let hierarchical layout assign levels
                )

            # Add edges
            for edge in graph_data.get('edges', []):
                rel_type   = edge.get('relationship_type', 'prerequisite')
                confidence = edge.get('confidence', 0.5)
                src = edge.get('source_id')
                tgt = edge.get('target_id')
                if not src or not tgt:
                    continue

                if rel_type == 'strict_prerequisite':
                    color  = '#2C3E50'
                    width  = 3
                    dashes = False
                    label  = 'required'
                elif rel_type == 'recommended_prerequisite':
                    color  = '#8E44AD'
                    width  = 2
                    dashes = True
                    label  = 'recommended'
                else:
                    color  = '#7F8C8D'
                    width  = 1
                    dashes = True
                    label  = 'related'

                edge_title = (
                    f"<b>{rel_type.replace('_', ' ').title()}</b><br>"
                    f"Confidence: {confidence:.0%}<br>"
                    f"{edge.get('reasoning', '')}"
                )

                net.add_edge(
                    src, tgt,
                    title=edge_title,
                    label=label,
                    color={'color': color, 'highlight': '#F39C12'},
                    width=width,
                    dashes=dashes
                )

            # ---- inject a legend + direction note into the HTML ----
            legend_html = f"""
<div style="position:fixed;top:10px;left:10px;background:rgba(255,255,255,0.95);
            border:1px solid #ccc;border-radius:8px;padding:12px 16px;
            font-family:Arial,sans-serif;font-size:13px;z-index:9999;
            box-shadow:2px 2px 8px rgba(0,0,0,0.15);max-width:260px">
  <b style="font-size:14px">{title}</b>
  <p style="margin:6px 0;color:#555;font-size:12px">
    &#8594; Arrow points from <b>prerequisite</b> to <b>dependent</b> concept<br>
    (top = foundational &nbsp;|&nbsp; bottom = advanced)
  </p>
  <hr style="margin:6px 0">
  <div><span style="display:inline-block;width:14px;height:14px;background:#E74C3C;border-radius:3px;vertical-align:middle"></span> High Importance</div>
  <div><span style="display:inline-block;width:14px;height:14px;background:#2980B9;border-radius:3px;vertical-align:middle"></span> Medium Importance</div>
  <div><span style="display:inline-block;width:14px;height:14px;background:#27AE60;border-radius:3px;vertical-align:middle"></span> Low Importance</div>
  <hr style="margin:6px 0">
  <div><span style="display:inline-block;width:28px;height:3px;background:#2C3E50;vertical-align:middle;margin-right:4px"></span> Strict Prerequisite</div>
  <div><span style="display:inline-block;width:28px;height:3px;background:#8E44AD;border-top:2px dashed #8E44AD;vertical-align:middle;margin-right:4px"></span> Recommended</div>
  <div><span style="display:inline-block;width:28px;height:3px;background:#7F8C8D;border-top:2px dotted #7F8C8D;vertical-align:middle;margin-right:4px"></span> Related</div>
</div>
"""

            output_path = self.viz_dir / f"{video_id}_interactive_graph.html"
            net.save_graph(str(output_path))

            # Inject legend into saved HTML
            html_text = output_path.read_text(encoding='utf-8')
            html_text = html_text.replace('<body>', '<body>\n' + legend_html, 1)
            output_path.write_text(html_text, encoding='utf-8')

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
