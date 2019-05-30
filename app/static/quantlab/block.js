// $(window).resize(function(){
//   var width = $(".bcard").width();
//   $(".bcard").css("height", width + "px");
//   $(".bcard_img").css({"width":width + "px", "height":width + "px"});
//   $(".bcard_like").css("font-size", width*0.15);
//   $(".bcard_more_btn").css("font-size", width*0.1);
//   $(".bcard_stat_value").css("font-size", width*0.2);
//   $(".bcard_stat_label").css("font-size", width*0.07);
// });
//
// $(window).trigger('resize');


var ncols;
var ncols_matcher = {1:'one', 2:'two', 3:'three', 4:'four', 5:'five', 6:'six'};
var ncols_keys = Object.keys(ncols_matcher).map(function(key){ return Number(key) });
var ncols_max = Math.max.apply(null, ncols_keys);
var ncols_min = Math.min.apply(null, ncols_keys);
var window_width = $(window).width();

if (window_width < 400) {
  ncols = 2;

} else if (window_width < 500) {
  ncols = 3;

} else {
  ncols = 4;
}


function resize_blocks(step) {
  if (step > 0) {
    ncols = Math.min(ncols+step, ncols_max);

  } else if (step < 0) {
    ncols = Math.max(ncols+step, ncols_min);
  }

  $('.blocks').attr('class', "blocks ui cards " + ncols_matcher[ncols]);
}


function load_blocks(where, url) {
  // resize_blocks(0);
  url = url + '&ncols=' + ncols_matcher[ncols];
  $(where).html('').load(url);
};


function load_block(img) {
  feather.replace();
  $(img).parents('.block').css('opacity', 1);
}

function block_more(event, icon) {
  event.stopPropagation();
  $(icon).siblings(".block-cover").css({"animation":"block-more 0.5s forwards"});
};

function block_cover_mouseleave(block_cover) {
  $(block_cover).css({"animation":"block-less 0.5s forwards"});
};

function block_cover_click(event, block_cover) {
  event.stopPropagation();
};

function block_click(block) {
  var url = $(block).attr("href");
  window.location.assign(url); //.replace()로 하면 history가 저장 안된다
};

function toggle_like(event, obj) {
  event.stopPropagation();
  var icon = $(obj).children(".block-like-icon");
  var state = icon.attr("state");
  // var bname = $(obj).parents(".block").attr("bname");

  var what;
  var type;
  var data;

  if ($(obj).parents(".block").is("[bname]")) {
    type = 'brand';
    what = $(obj).parents(".block").attr("bname");

  } else if ($(obj).parents(".block").is("[post-id]")) {
    type = 'post';
    what = $(obj).parents(".block").attr("post-id");
  }

  if (state=="like") {
    icon.attr({"state":"dontlike"});
    data = { type:type, dontlike:what };

  } else {
    icon.attr({"state":"like"});
    data = { type:type, like:what };
  };

  update_likes(data);
};

function update_likes(data) {
  $.ajax({
    // url: '/save_like/', //{% url 'save_like' %}, js파일에서 장고 템플릿은 안먹힌다
    url: '/update_likes/',
    async: true,
    type: 'GET',
    data: data,
    dataType: 'json',
    success: function(jqXHR) {
      if (!jqXHR.success) {
        alert("데이터를 처리하는데 문제가 발생하였습니다.");
      };
    }
  });
}
