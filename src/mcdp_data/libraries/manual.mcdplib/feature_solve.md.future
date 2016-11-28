


<mcdp-solve>
    <query>
        <model>`model</model>
        <points>        
        </points>
    </query>
    </points>
    </query>
    <plot>
    </plot>
</mcdp-solve>


result_like = dict(maintenance="R", cost="USD", mass='kg')
    what_to_plot_res = result_like
    what_to_plot_fun = dict(capacity="Wh", missions="[]")

    lib = MCDPLibrary()
    lib.add_search_dir('.')
    ndp = lib.load_ndp('batteries')

    data = solve_combinations(ndp, combinations, result_like)

    r = Report()

    plot_all_directions(r, queries=data['queries'], results=data['results'],
                        what_to_plot_res=what_to_plot_res,
                        what_to_plot_fun=what_to_plot_fun)
    r.to_html('out/batteries-c1.html')