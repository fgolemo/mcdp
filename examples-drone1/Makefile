

all:
	./example_drone1.py -c "clean; config echo 1; rparmake"

solve0:
	mcdp-solve --out=out/drone0 -d models/drone0 battery '<1 hour, 0.1 kg, 1.0 W>'

solve1a:
	mcdp-solve --out=out/drone1/sa -d models/drone1 drone "<0s, 0kg>"

solve1b:
	mcdp-solve --out=out/drone1/sb -d models/drone1 drone "<1 hour, 0kg>"


plots: plot1 plot2 plot3

plot1:
	mcdp-plot --out=out/drone1 -d models/drone1 drone 

plot2:
	mcdp-plot --out=out/drone2 -d models/drone2 drone2_cost 

plot3:
	mcdp-plot --out=out/drone3 -d models/drone3 drone3

	 # {'id': 'drone1', 'dir': 'models/drone1', 'model': 'drone'},
  #           {'id': 'drone2', 'dir': 'models/drone2', 'model': 'drone2_cost'},
  #           {'id': 'drone3', 'dir': 'models/drone3', 'model': 'drone3'},
  #       ]