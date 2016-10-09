from contracts import contract
from mcdp_posets import PosetProduct, Rcomp
from mocdp.memoize_simple_imp import memoize_simple
import numpy as np


class CommonStats():
    
    def __init__(self, data):
        self.data = data
        all_num_solutions = []
        all_num_implementations = []
        
        for query, query_results, implementations in zip(data['queries'], data['results'], data['implementations']):  # @UnusedVariable
            num_solutions = len(query_results)
                
            num_implementations = sum([len(x) for x in implementations])
            
            all_num_implementations.append(num_implementations)
            all_num_solutions.append(num_solutions)

        self.all_num_solutions = np.array(all_num_solutions)
        self.all_num_implementations = np.array(all_num_implementations)
        
        self.one_solution = self.all_num_solutions == 1
        self.multiple_solutions = self.all_num_solutions > 1
        self.is_not_feasible = self.all_num_solutions == 0
        self.is_feasible =  self.all_num_solutions> 0
        self.one_implementation = self.all_num_implementations == 1
        self.multiple_implementations = self.all_num_implementations > 1
        
    @memoize_simple
    def get_functionality(self, fname):
        res  = []
        data = self.data
        for query, query_results, implementations in zip(data['queries'], data['results'], data['implementations']):  # @UnusedVariable
            v = query[fname]
            res.append(v)
        return np.array(res) 
    
    @memoize_simple
    def get_min_resource(self, rname):
        data = self.data
        res  = []
        for query, query_results, implementations in zip(data['queries'], data['results'], data['implementations']):  # @UnusedVariable
            num_solutions = len(query_results)
        
            if num_solutions == 0:
                v = np.nan
            else:
                v = np.min([_[rname] for _ in query_results])
            res.append(v)
        return np.array(res) 
                
    @contract(rnames='seq(str)',
              fnames='seq(str)')        
    def iterate(self, fnames, rnames):
        fs = []
        rs = []      

        data = self.data
        def extract_fun(query):
            return tuple([query[fname] for fname in fnames]) 
        
        def extract_res(query_result):
            return tuple([query_result[rname] for rname in rnames]) 
            
        for query, query_results in zip(data['queries'], data['results']):
            fs.append(extract_fun(query))
            rs.append(map(extract_res, query_results))
            
        return fs, rs 
    
#     @contract(rnames='seq(str)',
#               fnames='seq(str)')        
#     def iterate_ordered(self, fnames, rnames):
#         fs, rs = self.iterate(fnames, rnames)
#         
#         indices = range(len(fs))
#         order = sorted(indices, key)
#         assert len(fnames) == 2
#         P = PosetProduct((Rcomp(),) * 2)
#          
#         order = np.argsort(fs, key=P.leq)
#         
#         fs = [fs[i] for i in order]
#         rs = [rs[i] for i in order]
#         return fs, rs
#     
#                 