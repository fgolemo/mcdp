from .figure_interface import MakeFigures
from .formatters import TextFormatter, GGFormatter


__all__ = [
    'MakeFiguresDP',
]

class MakeFiguresDP(MakeFigures):
    def __init__(self, dp):
        self.dp = dp
        
        aliases = {
            'dp_graph_flow': 'dp_graph_flow_TB',
            'dp_graph_tree': 'dp_graph_tree_TB',
            'dp_graph_tree_compact': 'dp_graph_tree_compact_TB',
        }
        
        figure2function = {
            'dp_graph_flow_LR': (DPGraphFlow, dict(direction='LR')), 
            'dp_graph_flow_TB': (DPGraphFlow, dict(direction='TB')),
            'dp_graph_tree_LR': (DPGraphTree, dict(direction='LR', compact=False)), 
            'dp_graph_tree_TB': (DPGraphTree, dict(direction='TB', compact=False)),
            'dp_graph_tree_compact_LR': (DPGraphTree, dict(direction='LR', compact=True)), 
            'dp_graph_tree_compact_TB': (DPGraphTree, dict(direction='TB', compact=True)),
            'dp_repr_long': (DP_repr_long, dict()),
        }
        
        MakeFigures.__init__(self, aliases=aliases, figure2function=figure2function)
    
    def get_dp(self):
        return self.dp
    

class DP_repr_long(TextFormatter):
    
    def get_text(self, mf):
        dp = mf.get_dp()
        return dp.repr_long()
    

    
class DPGraphFlow(GGFormatter):
    def __init__(self, direction):
        self.direction = direction
        
    def get_gg(self, mf):
        dp = mf.get_dp()
        from mcdp_report.dp_graph_flow_imp import dp_graph_flow
        gg = dp_graph_flow(dp, direction=self.direction)
        return gg
    
class DPGraphTree(GGFormatter):
    def __init__(self, compact, direction):
        self.compact = compact
        self.direction = direction
        
    def get_gg(self, mf):
        dp = mf.get_dp()
        from mcdp_report.dp_graph_tree_imp import dp_graph_tree
        gg = dp_graph_tree(dp, imp=None, compact=self.compact, direction=self.direction)
        return gg
