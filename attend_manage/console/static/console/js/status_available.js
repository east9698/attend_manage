$(function(){
  $("#enter").on('click', function(event){
    event.preventDefault(); // form機能の停止
    alert("request processing...");
    status = false;

    if ($(this).prop("name")=="enter") {
      status = true;
    }else if ($(this).prop("name")=="exit") {
      status = false;
    }

    request_data = {
      "status": status
    };
    //console.log(JSON.stringify(data));
    $.ajax({
      url: "status_change/",　// なぜか{% url 'status_change' %}とすると、404になってしまう。。。
      method: "POST",
      data: request_data // 連想配列をJSONに変換しなくて良い見たい・・・
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

      if (responce['error'] === "not_changed") {
        alert(`既に入室しています。 (status = ${jqXHR.status})`);
        return(0);
      } else if ('error' in responce) {
        alart("サーバ上で予期せぬエラーが発生しました。\nもう一度試すか、管理者にご連絡ください。");
        return(1);
      } else {
        console.log(responce);
        alert(`正常に処理しました。(status = ${jqXHR.status})`);
        $("#enter").prop('disabled', true);
        $("#exit").prop('disabled', false);
        $("#status").html("在室");
      }
    })
    .fail(function(jqXHR, textStatus, errorThrown){
      alert(`通信エラーが発生しました。(status = ${jqXHR.status})\nもう一度試すか、管理者にご連絡ください。`);
    });
  });

  $("#exit").on('click', function(event){
    event.preventDefault(); // form機能の停止
    alert("request processing...");
    status = false;

    if ($(this).prop("name")=="enter") {
      status = true;
    }else if ($(this).prop("name")=="exit") {
      status = false;
    }

    request_data = {
      "status": status
    };
    $.ajax({
      url: "status_change/",　// なぜか{% url 'status_change' %}とすると、404になってしまう。。。
      method: "POST",
      data: request_data // 連想配列をJSONに変換しなくて良い見たい・・・
    })
    .done(function(responce, textStatus, jqXHR){

      if (responce['error'] === "not_changed") {
        alert(`既に退室しています。 (status = ${jqXHR.status})`);
        return(0);
      } else if ('error' in responce) {
        alart("サーバ上で予期せぬエラーが発生しました。\nもう一度試すか、管理者にご連絡ください。");
        return(1);
      } else {
        console.log(responce);
        alert(`正常に処理しました。(status = ${jqXHR.status})`);
        $("#enter").prop('disabled', false);
        $("#exit").prop('disabled', true);
        $("#status").html("不在");
      }
    })
    .fail(function(jqXHR, textStatus, errorThrown){
      alert(`通信エラーが発生しました。(status = ${jqXHR.status})\nもう一度試すか、管理者にご連絡ください。`);
    });
  });

});
