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

function bcard_more(event, icon) {
  event.stopPropagation();
  $(icon).siblings(".bcard_cover").css({"animation":"bcard_more 0.5s forwards"});
};

function bcard_cover_mouseleave(bcard_cover) {
  $(bcard_cover).css({"animation":"bcard_less 0.5s forwards"});
};

function bcard_cover_click(event, bcard_cover) {
  event.stopPropagation();
};

function bcard_click(bcard) {
  var url = $(bcard).attr("href");
  window.location.assign(url); //.replace()로 하면 history가 저장 안된다
};

function toggle_like(event, obj) {
  event.stopPropagation();
  var icon = $(obj).children(".icon");
  var state = icon.attr("state");
  var bname = $(obj).parents(".bcard").attr("bname");
  var data;

  if (state=="like") {
    icon.attr({"state":"dontlike", "class":"bcard_dontlike_icon outline heart icon"});
    icon.css({"opacity":0.5, "color":"gainsboro"});
    data = {dontlike:bname};

  } else {
    icon.attr({"state":"like", "class":"bcard_like_icon yellow heart icon"});
    icon.css({"opacity": 1, "color": ""});
    data = {like:bname};
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
