const template_feedblock = ({id, image}) => `
  <div class="block-container column">
    <div class="block ui fluid card" feed-id="${id}" href="${id}" onclick="block_click(this)">
      <div class="block-base">
        <img class="block-img" src="https://storage.googleapis.com/getch-245810.appspot.com/${image}" style="object-fit:cover;" onload="load_block(this)">
      </div>
    </div>
  </div>
`;


const template_feed = function({id, author_image, content, image, hashtags, pages_image, timestamp}) {
  var template_hashtags;
  var template_image;
  var template_pages_image;

  if (hashtags.length == 0) {
    template_hashtags = '';

  } else {
    var hashtags_list = hashtags.map((hashtag) => `<a class="hashtag ui tiny label" href="#">${hashtag}</a>`).join('');
    template_hashtags = `<p>${hashtags_list}</p>`;
  }

  if (image == '') {
    template_image = '';

  } else {
    template_image = `
      <p>
        <img src="https://storage.googleapis.com/getch-245810.appspot.com/${image}" style="max-width:80%;" class="ui centered image">
      </p>
    `;
  }

  if (pages_image.length == 0) {
    template_pages_image = '';

  } else {
    template_pages_image = pages_image.map(({name, image}) => `
      <a class="item" href="/page/${name}" style="background:none;padding:5px;">
        <img class="ui circular image" src="https://storage.googleapis.com/getch-245810.appspot.com/${image}" style="object-fit:contain;width:30px;height:30px">
      </a>
    `).join('');
  }

  return `
    <div class="detailsec ui padded segment">
      <div class="feed-menu ui secondary icon menu" style="background:none;">
        <div class="item" style="background:none;padding:5px;">
          <img class="ui circular image" src="https://storage.googleapis.com/getch-245810.appspot.com/${author_image}" style="object-fit:cover;width:30px;height:30px">
        </div>

        ${template_pages_image}

        <div class="right compact menu">
          <a class="item" action="feed_like" onclick="toggle_action(this)">
          </a>

          <a class="item">
            <div class="share-dropdown top right pointing ui dropdown">
              <i class="large share alternate icon"></i>
              <div class="menu">
                <div class="item" data-value="kakaotalk">kakaotalk</div>
                <div class="item" data-value="facebook">facebook</div>
                <div class="item" data-value="instagram">instagram</div>
                <div class="item" data-value="linkurl">link url</div>
              </div>
            </div>
          </a>

        </div>
      </div>

      <p>${content}</p>

      ${template_image}
      ${template_hashtags}

      <p style="font-size:10px;">${timestamp}</p>
      <div class="ui divider" style="background:none;"></div>
    </div>
  `;
}


const template_pageblock = function({id, page__name, page__image, master__image}) {
  var template_master;

  if (master__image == undefined) {
    template_master = '';

  } else {
    template_master = `
      <div class="block-master">
        <img class="ui circular image" src="https://storage.googleapis.com/getch-245810.appspot.com/${master__image}" style="object-fit:cover;width:30px;height:30px;border:medium solid white">
      </div>
    `
  }

  return `
    <div class="block-container column">
      <div class="block ui fluid card" page-id="${id}" href="/page/${page__name}" onclick="block_click(this)">
        <div class="block-base">
          <img class="block-img" src="https://storage.googleapis.com/getch-245810.appspot.com/${page__image}" style="object-fit:contain;" onload="load_block(this)">
          ${template_master}
        </div>
      </div>
    </div>
  `;
}


function ContentLoader(options) {
  feather.replace();
  var template;
  var data = options.data;
  var where = options.where;
  var n_init = options.n_init;
  var n_next = options.n_next;

  switch (options.type) {
    case 'feedblock':
      template = template_feedblock;
      break;

    case 'feed':
      template = template_feed;
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