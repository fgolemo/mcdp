
all: solve plot

clean:
	rm -rf out/ _cached

solve:
	mcdp-solve --out=out/solve1 --plot --imp -d . drone "<0s, 0kg, 0W>"

plot:
	mcdp-plot --out=out -d . Actuation
	mcdp-plot --out=out -d . Drone

