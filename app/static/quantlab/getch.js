const template_feedblock = ({id, feed_image}) => `
  <div class="block-container column">
    <div class="block ui fluid card" feed-id="${id}" href="${id}" onclick="block_click(this)">
      <div class="block-base">
        <img class="block-img" src="https://storage.googleapis.com/getch-245810.appspot.com/${feed_image}" style="object-fit:cover;" onload="load_block(this)">
      </div>
    </div>
  </div>
`;

const template_feed = ({}) => `
  <div class="detailsec ui padded segment">
    <div class="feed-menu ui secondary icon menu" style="background:none;">
      <div class="item" style="background:none;padding:5px;">
        {% include "app/user_avatar.html" with profile=feed.author %}
      </div>

      <div class="right compact menu">
        <a class="item" action="feed_like" onclick="toggle_action(this)">
          {% include "app/action_icon.html" with action_type="like" obj=post %}
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

    <p>{{ feed.content }}</p>

    {% if feed.feed_image %}
    <p>
      <img src='{{ feed.feed_image.url }}' style="max-width:80%;" class="ui centered image">
    </p>
    {% endif %}

    <p>
    {% for hashtag in feed.hashtags.all %}
      <a class="hashtag ui tiny label" href="#">{{ hashtag }}</a>
    {% endfor %}
    </p>

    <p style="font-size:10px;">{{ feed.timestamp }}</p>
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
