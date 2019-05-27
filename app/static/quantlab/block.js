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


var ncols = 4;
var ncols_max = 6;
var ncols_min = 1;
var ncols_matcher = {1:'one', 2:'two', 3:'three', 4:'four', 5:'five', 6:'six'};

function resize_block(step) {
  if (step > 0) {
    ncols = Math.min(ncols+step, ncols_max);

  } else if (step < 0) {
    ncols = Math.max(ncols+step, ncols_min);
  }

  $('.blocks').attr('class', "blocks ui cards " + ncols_matcher[ncols]);
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
  var bname = $(obj).parents(".block").attr("bname");
  var data;

  if (state=="like") {
    icon.attr({"state":"dontlike"});
    data = { dontlike:bname };

  } else {
    icon.attr({"state":"like"});
    data = { like:bname };
  };

  $.ajax({
    url: '/save_like/', //{% url 'save_like' %}, js파일에서 장고 템플릿은 안먹힌다
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
};


$(document).ready(function(){
  $(".block").transition({
    animation  : 'fade',
    duration   : '1s',
    onComplete : function() {
      // console.log(1);
    }
  });
})
