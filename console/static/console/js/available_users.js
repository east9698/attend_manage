$(function(){
  $("#available_users_list .result").on('click', function(event){
    event.preventDefault(); // form機能の停止
    alert("request processing...");

    /*request_data = {
      "status": status
    };*/
    //console.log(JSON.stringify(data));
    $.ajax({
      url: "status_all/",　// なぜか{% url 'status_change' %}とすると、404になってしまう。。。
      method: "POST",
      cache: false
      //data: request_data // 連想配列をJSONに変換しなくて良い見たい・・・
      //dataType: "json", // 返信データの形式
      //timeout : "5000", // 5秒待機
      //processData: false,
      //contentType: false,
      //data: {"user" : "higashi","status" : $(this).prop("name")}

      /*beforeSend: function(xhr, settings) {         //リクエスト送信前の処理,CSRFTokenを設定
         xhr.setRequestHeader("X-CSRFToken", $("input[name='csrfmiddlewaretoken']").val());
      }*/
    })
    .done(function(responce, textStatus, jqXHR){

      if ('error' in responce) {

        //alert("サーバ上で予期せぬエラーが発生しました。\nもう一度試すか、管理者にご連絡ください。");
        $(innner_table).empty();
        return(0);

      } else {

        alert(`正常に処理しました。(status = ${jqXHR.status})`);

        console.log(responce.available_users[0].username);
        //alert(responce["available_users"][0]["username"]);

        var innner_table = "#available_users_list > table > tbody";
        $(innner_table).empty();
        for (var i = 0; i < responce.available_users.length; i++) {
          var username = responce.available_users[i].username;
          var time_in = responce.available_users[i].time_in;
          $(innner_table).html($(innner_table).html() + "<tr>\n<th>" + username + "</th>\n<td>" + time_in + "</td>\n</tr>");
        }
      }
    })
    .fail(function(jqXHR, textStatus, errorThrown){
      alert(`通信エラーが発生しました。(status = ${jqXHR.status})\nもう一度試すか、管理者にご連絡ください。`);
    });
  });



});
