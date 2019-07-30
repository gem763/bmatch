const template_feedblock = ({id, image}) => `
  <div class="block-container column">
    <div class="block ui fluid card" feed-id="${id}" href="${id}" onclick="block_click(this)">
      <div class="block-base">
        <img class="block-img" src="https://storage.googleapis.com/getch-245810.appspot.com/${image}" style="object-fit:cover;" onload="load_block(this)">
      </div>
    </div>
  </div>
`;

const template_pageblock = ({id, page__image}) => `
  <div class="block-container column">
    <div class="block ui fluid card" page-id="${id}" href="${id}" onclick="block_click(this)">
      <div class="block-base">
        <img class="block-img" src="https://storage.googleapis.com/getch-245810.appspot.com/${page__image}" style="object-fit:contain;" onload="load_block(this)">
      </div>
    </div>
  </div>
`;



function ContentLoader(options) {
  var template;
  var data = options.data;
  var where = options.where;
  var n_init = options.n_init;
  var n_next = options.n_next;

  switch (options.type) {
    case 'feedblock':
      template = template_feedblock;
      break;

    case 'pageblock':
      template = template_pageblock;
      break;
  }

  $(where).append(data.splice(0, n_init).map(template).join(''));

  $(where).visibility({
    once: false,
    observeChange: true,
    onBottomVisible: function() {
      $(where).append(data.splice(0, n_next).map(template).join(''));
    }
  });
}


function load_block(img) {
  $(img).parents('.block').css('opacity', 1);
}

function block_click(block) {
  var url = $(block).attr("href");
  window.location.assign(url); //.replace()로 하면 history가 저장 안된다
}



// var ncols = 3;
// var ncols_matcher = {1:'one', 2:'two', 3:'three', 4:'four', 5:'five', 6:'six'};
// var ncols_keys = Object.keys(ncols_matcher).map(function(key){ return Number(key) });
// var ncols_max = Math.max.apply(null, ncols_keys);
// var ncols_min = Math.min.apply(null, ncols_keys);
// var window_width = $(window).width();
//
// function resize_blocks(where, step) {
//   if (step > 0) {
//     ncols = Math.min(ncols+step, ncols_max);
//
//   } else if (step < 0) {
//     ncols = Math.max(ncols+step, ncols_min);
//   }
//
//   $(where).attr('class', "ui " + ncols_matcher[ncols] + " column grid");
// }
