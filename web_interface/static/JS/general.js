function clear_out_contents() {
  document.getElementById("input_form").value = "";
  document.getElementById("response").innerHTML = "";
  document.getElementById("response_card").style.display = "none";
  document.getElementById("message").innerHTML = "";
}


document.getElementById("clear_button").onclick = function () {
  clear_out_contents();
};

document.getElementById("schema_button").onclick = function () {
  retrieve_schema();
};

$('.dropdown-item').click(function () {
  document.getElementById("db_dropdown_button").innerHTML = $(this).text();
  update_schema($(this).text());
  send_db_selection($(this).text());
});

document.getElementById("convert_button").onclick = function () {
  let input_text = document.getElementById("input_form").value.trim();
  let db = document.getElementById("db_dropdown_button").textContent;

  // console.log(input_text);
  if (input_text.length > 0 && db.trim() != "Database selection") {
    $.ajax({
      type: 'post',
      url: '/evaluate',
      data: JSON.stringify({
        "data": input_text,
        "db": db
      }),
      contentType: "application/json",
      timeout: 5000,
      success: function (result) {
        document.getElementById("message").innerHTML = "";
        document.getElementById("response_card").style.display = "block";
        document.getElementById("response").innerHTML = result.result;
      },
      error: function (result) {
        document.getElementById("message").innerHTML = "An error has occured during evaluation of the query...";
      },
    });
  } else {
    document.getElementById("message").innerHTML = "Input something first and make a database selection";
  }
};

function send_db_selection(new_db) {
  document.getElementById("convert_button").disabled = true;
  $.ajax({
    type: 'post',
    url: '/db_change',
    data: JSON.stringify({
      "db": new_db
    }),
    contentType: "application/json",
    timeout: 5000,
    success: function (result) {
      document.getElementById("message").innerHTML = "";
      document.getElementById("convert_button").disabled = false;
    },
    error: function (result) {
      document.getElementById("message").innerHTML = "An error has occured during loading of saved models...";
    },
  });
}

function update_schema(new_db) {
  let schema_div = document.getElementById("schema_layout");
  let ex_question_div = document.getElementById("ex_question_layout");

  let schema_card = document.getElementById("schema_card");

  if (schema_card.style.display != "none") {
    $.ajax({
      type: 'post',
      url: '/schema',
      data: JSON.stringify({
        "db": new_db
      }),
      contentType: "application/json",
      timeout: 5000,
      success: function (result) {
        document.getElementById("message").innerHTML = "";
        let text = '<ul>';
        for (x in result.result) {
          text += '<li>' + x + '<ul>';
          for (item in result.result[x]) {
            text += '<li>' + result.result[x][item] + '</li>';
          }
          text += '</ul>';
          text += '</li>';

        }
        text += '</ul>';
        schema_div.innerHTML = text;

        let text2 = '<ol>';
        for (i in result.questions) {
          text2 += '<li>' + result.questions[i] + '</li>';
        }
        text2 += '</ol>';
        ex_question_div.innerHTML = text2;
      },
      error: function (result) {
        document.getElementById("message").innerHTML = "An error has occured while retrieving schema...";
      },
    });
  }
}

function retrieve_schema() {
  let schema_div = document.getElementById("schema_layout");
  let ex_question_div = document.getElementById("ex_question_layout");
  
  let schema_card = document.getElementById("schema_card");
  let schema_button = document.getElementById("schema_button");
  let db = document.getElementById("db_dropdown_button").textContent;

  if (schema_card.style.display == "none" && db.trim() != "Database selection") {
    schema_button.innerHTML = "Hide schema";
    $.ajax({
      type: 'post',
      url: '/schema',
      data: JSON.stringify({
        "db": db
      }),
      contentType: "application/json",
      timeout: 5000,
      success: function (result) {
        document.getElementById("message").innerHTML = "";
        let text = '<ul>';
        for (x in result.result) {
          text += '<li>' + x + '<ul>';
          for (item in result.result[x]) {
            text += '<li>' + result.result[x][item] + '</li>';
          }
          text += '</ul>';
          text += '</li>';

        }
        text += '</ul>';
        schema_div.innerHTML = text;

        let text2 = '<ol>';
        for (i in result.questions) {
          text2 += '<li>' + result.questions[i] + '</li>';
        }
        text2 += '</ol>';
        ex_question_div.innerHTML = text2;

      },
      error: function (result) {
        document.getElementById("message").innerHTML = "An error has occured while retrieving schema...";
      },
    });
    schema_card.style.display = "block";
  } else {
    schema_button.innerHTML = "Show schema";
    schema_card.style.display = "none";
    schema_div.innerHTML = "";
  }
}