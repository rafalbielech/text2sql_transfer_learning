function clear_out_contents(){
    document.getElementById("input_form").value = "";
    document.getElementById("response").innerHTML = "";
}

document.getElementById("clear_button").onclick = function () {
    clear_out_contents();
};

document.getElementById("convert_button").onclick = function () {
    let input_text = document.getElementById("input_form").value.trim();
    console.log(input_text);
    if (input_text.length > 0){
        $.ajax({
            type: 'post',
            url: '/evaluate',
            data: JSON.stringify({"data" : input_text}),
            contentType: "application/json",
            timeout : 5000,
            success: function(result) {
              document.getElementById("response").innerHTML = result.result;
            },
            error: function(result) {
              alert("ERROR");
            },
          });
    }
    else {
      alert("Input something first");
    }
};