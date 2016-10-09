from mcdp_ipython_utils.plotting import color_functions, color_resources
from mcdp_posets import Coproduct1Labels, SpaceProduct, FiniteCollectionAsSpace
import numpy as np
from plot_utils import ieee_spines_zoom3, plot_field


fig = dict(figsize=(4.5, 4))

def get_choice(I, imp): 
    # I.belongs(imp)
    
    if isinstance(I, Coproduct1Labels):
        index, xi = I.unpack(imp)  # @UnusedVariable
        label = I.labels[index]
        return label, FiniteCollectionAsSpace(I.labels)
    
    if isinstance(I, SpaceProduct):
        for S, s  in zip(I.subs, imp):
            res = get_choice(S, s)
            if res is not None:
                return res
    
    return None
        
    
def compute_discrete_choices(data):
    I = data['I']
    #print I.repr_long()

    all_discrete_choices = []
    for query, query_results, implementations in zip(data['queries'], data['results'], data['implementations']):  # @UnusedVariable
    
        discrete_choices = set()
        for ms in implementations:
            for m in ms:
                choice = get_choice(I, m)
                assert choice is not None, m
                choice, _choices = choice
                discrete_choices.add(choice)
        discrete_choices = "-".join(sorted(discrete_choices))
        all_discrete_choices.append(discrete_choices)
    return all_discrete_choices

def figure_discrete_choices2(r, data, cs, fname1, fname2):
    
    num_solutions = cs.all_num_implementations
    all_discrete_choices = compute_discrete_choices(data)
    
    possible = ['', 'LCO', 
                'LFP', 
                'NiCad',
                'NiMH',
                'LiPo',
                'LCO-LiPo-NiMH',
                'LCO-LiPo-NiCad',
                'LCO-LFP-LiPo-NiCad',
                'LCO-LFP-LiPo',
                'LCO-LFP-LiPo-NiMH',
                'LCO-LiPo-NiCad-NiMH',
                'LCO-LFP-LiPo-NiCad-NiMH',
                'LCO-LiPo',
                'LCO-LFP',
                'LCO-LFP-NiMH',
                'LCO-NiMH',
                 'LCO-NiCad',
                 'LCO-NiCad-NiMH', 
                 'LCO-LFP-NiCad', 
                 'LCO-LFP-NiCad-NiMH', 
                 'LCO-NiCad-NiMH']    
    possible_this = sorted(np.unique(all_discrete_choices))
    for p in possible_this:
        if not p in possible:
            msg = 'Did not anticipate %r as an option.' % p
            raise ValueError(msg)

    choice_as_int = np.zeros(dtype='int', shape=len(all_discrete_choices))
    for i, x in enumerate(all_discrete_choices):
        choice_as_int[i] = possible.index(x)
    
    def do_axes(pylab):
        from mcdp_ipython_utils.plotting import set_axis_colors    
        set_axis_colors(pylab, color_functions, color_functions)
    
    with r.plot('choice_as_int', **fig) as pylab:
  
        ieee_spines_zoom3(pylab)
  
        x = cs.get_functionality(fname1)
        y = cs.get_functionality(fname2)
        z = choice_as_int
        plot_field(pylab, x, y, z, cmap='viridis', vmin=0, vmax=len(possible))
        pylab.title('choice_as_int',  y=1.08)
        do_axes(pylab)

    possible_indiv = set()
    for p in possible:
        for x in p.split('-'):
            possible_indiv.add(x)
    
        
    f = r.figure()
    for p in sorted(possible_indiv):
        if not p: continue
        
        feasible = np.array([p in _ for _ in all_discrete_choices])
        with f.plot('where_%s' % p, **fig) as pylab:
            
            ieee_spines_zoom3(pylab)
  
            x = cs.get_functionality(fname1)
            y = cs.get_functionality(fname2)
            
            AND = np.logical_and
            is_best = AND(feasible, num_solutions == 1)
            is_one_of_two = AND(feasible, num_solutions == 2)
            is_one_of_three = AND(feasible, num_solutions == 3)
            is_one_of_four_or_more = AND(feasible, num_solutions >= 4)
            
            grey = '#bbbbbb'
            color_infeasible = 'red'
            pylab.plot(x[cs.is_feasible], 
                       y[cs.is_feasible], '.', markersize=2, 
                       markerfacecolor=grey,
                       markeredgecolor='none', color='none', 
                       clip_on=False)
            pylab.plot(x[cs.is_not_feasible], 
                       y[cs.is_not_feasible], '.', markersize=2, 
                       markerfacecolor=color_infeasible,
                       markeredgecolor='none', color='none', 
                       clip_on=False)

            def plot(where, marker, color):            
                markersize = 3.5
                pylab.plot(x[where], y[where], marker, markersize=markersize, 
                           markeredgecolor='none',
                           markerfacecolor=color, 
                           color='none', clip_on=False)
                
            plot(is_best, 'o', 'black')
            plot(is_one_of_two, 'd', '#000088')
            plot(is_one_of_three, '>','#880000')
            plot(is_one_of_four_or_more,'s', '#880088')
            
            pylab.title('%s' % p,  y=1.08)
            do_axes(pylab)
    
    r.text('possible', possible) 
    r.text('text_choice_as_int', choice_as_int)  
    r.text('choices', all_discrete_choices)
