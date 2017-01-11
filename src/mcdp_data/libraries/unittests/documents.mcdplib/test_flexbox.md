

<style type="text/css">
    div#one {
  display: flex;
  justify-content: space-around;
  border: solid 1px;
}

.image {
  display: inline-block;
  width: 10em;
  height: 10em;
  background-color: red;
}

#image2 {
  width: 5em;
  height: 5em;
}

div div {
  border: 3px solid blue;
  display: cell;
  vertical-align: middle;
}

</style>
  
Unfortunately this is not supported by Prince (they say early 2017).

<div id="one">
  <div><span class="image" id="image1"></span></div>
  <div><span class="image" id="image2"></span></div>
</div>

  