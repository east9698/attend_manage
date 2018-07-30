$(function(){

  $("button[name='enter']").on('click', function(event){
    event.preventDefault(); // form機能の停止
    alert("ok");
    $.ajax({
      url: /status_change/,
      method: POST,
      data: $(this).prop("name")
    })
    .done(function(data){
      data["proc_status"] ? alert("正常に入室処理されました。") : alart("サーバーでエラーが発生しました。\nもう一度試すか、管理者にご連絡ください。");

    })
  })
  var length = $("p").length;
  console.log(length);
});
