outd=out/

all: racecar1 duckiebot1 duckiebot0 Turtlebot2 

clean:
	rm -rf $(outd)	
	rm -rf _cached
	
racecar1:
	mcdp-plot --cache --out $(outd) --plots ndp_graph_enclosed -D ../.. -d . racecar1

duckiebot1:
	mcdp-plot --cache --out $(outd) --plots ndp_graph_enclosed -D ../.. -d . duckiebot1

duckiebot0:
	mcdp-plot --cache --out $(outd) --plots ndp_graph_enclosed -D ../.. -d . duckiebot0

Turtlebot2:
	mcdp-plot --cache --out $(outd) --plots ndp_graph_enclosed -D ../.. -d . Turtlebot2
