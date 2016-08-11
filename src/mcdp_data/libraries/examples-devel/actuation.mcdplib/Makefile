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


duckiebot_sol00:
	mcdp-plot --cache --out $(outd) --plots ndp_graph_enclosed -D ../.. -d . duckiebot_sol00


# mcdp-solve -D ../../ -d . DaguChassis '< <`RigidBodyID: rb1, 0.1 m/s, 10 minutes>, < S(payload):*, 0 g, <0m,0m,0m>, `RigidBodyID: rb1 >, < S(payload):*, 0 g, <0m,0m,0m>, `RigidBodyID: rb1 >>'