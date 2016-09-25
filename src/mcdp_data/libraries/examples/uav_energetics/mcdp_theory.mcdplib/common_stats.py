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
                
                
                
                