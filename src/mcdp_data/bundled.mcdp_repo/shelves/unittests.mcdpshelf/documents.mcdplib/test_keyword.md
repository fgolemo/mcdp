
##  only f

    <col2>
        <p>This is <f>just using the f</f> and <r>the r element</r>.</p>
        <p>This is <span style='color:darkgreen'>just using the f</span> 
        and <span style='color:darkred'>the r element</span>.</p>
    </col2>

<col2 class='headers-row1'>
    <p>Actual</p><p>Expected</p>
    <p>This is <f>just using the f</f> and <r>the r element</r>.</p>
    <p>This is <span style='color:darkgreen'>just using the f</span> 
    and <span style='color:darkred'>the r element</span>.</p>
</col2>

## f inside k

    <col2>
        <p>This is <k><f>f inside k</f></k> and <f>r inside k</f>.</p>
        <p>This is <code class="keyword" style='color:darkgreen'>f inside k</code> 
        and <code class="keyword" style='color:darkred'>r inside k</code>.
    </col2>

<col2 class='headers-row1'>
    <p>Actual</p><p>Expected</p>
    <p>This is <k><f>f inside k</f></k> and <k><r>r inside k</r></k>.</p>
    <p>This is <code class="keyword" style='color:darkgreen'>f inside k</code> 
    and <code class="keyword" style='color:darkred'>r inside k</code>.</p>
</col2>
