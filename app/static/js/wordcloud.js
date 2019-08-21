function WordCloud(options) {
  var margin = {top: 0, right: 0, bottom: 0, left: 0},
           w = options.width - margin.left - margin.right,
           h = 0.5*options.width - margin.top - margin.bottom;

  // create the svg
  var svg = d3.select(options.container).append("svg")
              .attr('height', h + margin.top + margin.bottom)
              .attr('width', w + margin.left + margin.right)

  // set the ranges for the scales
  var xScale = d3.scaleLinear().range([0.01*w, 0.11*w]); // [.., 100] 으로 하면, 너무 큰 텍스트는 안보이게 된다

  var focus = svg.append('g').attr("transform", "translate(" + [w/2, h/2] + ")")
  // var colorMap = ['red', '#a38b07'];
  var fill = d3.scaleOrdinal(d3.schemeCategory10);

  // seeded random number generator
  var arng = new alea('hello.');

  var word_entries = d3.entries(options.data);

  xScale.domain(d3.extent(word_entries, function(d) { return d.value; }));
  makeCloud();


  function makeCloud() {
    d3.layout.cloud().size([w, h])
             .timeInterval(20)
             .words(word_entries)
             .rotate(0)
             .fontSize(function(d) {
               return xScale(+d.value);
             })
             .text(function(d) { return d.key; })
             // .font("Jost")
             .font("Noto Sans KR")
             // .font("Impact")
             .random(arng)
             .on("end", draw)
             // .on("end", function(output) {
             //   // sometimes the word cloud can't fit all the words- then redraw
             //   // https://github.com/jasondavies/d3-cloud/issues/36
             //   if (word_entries.length !== output.length) {
             //     console.log("not all words included- recreating");
             //     makeCloud();
             //     return undefined;
             //   } else { draw(output); }
             // })
             .start();

    d3.layout.cloud().stop();
  };


  function draw(words) {
    focus.selectAll("text")
         .data(words)
         .enter().append("text")
         .style("font-size", function(d) {
           return xScale(d.value) + "px";
         })
         // .style("font-family", "Impact")
         // .style("font-family", "Jost")
         .style("font-family", "Noto Sans KR")
         .style("font-weight", "400")
         .style("fill", function(d, i) { return fill(i); })
         .attr("text-anchor", "middle")
         .attr("transform", function(d) { return "translate(" + [d.x, d.y] + ")rotate(" + d.rotate + ")"; })
         .text(function(d) { return d.key; })
         .on('mouseover', handleMouseOver)
  };


  function handleMouseOver(d) {
    tippy(this, {
      // content: "<a target='_blank' href='https://www.google.com/search?q=" + d.key + "'><strong>" + d.key + "</strong> 검색하기</a>",
      content: "<a href='/journey/" + d.key + "'><strong>" + d.key + "</strong> 검색하기</a>",
      arrow: true,
      arrowType: 'round',
      theme: 'light',
      interactive: true,
      placement: 'top',
      size: 'large',
      distance: 20,
      followCursor: 'initial',
      //followCursor: true,
      trigger: 'click',
    })
  };
}
