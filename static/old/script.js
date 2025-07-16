
// index page

var currentPage = 2; // Track the current page number
var itemsPerPage = 2; // Number of items to load per page
const delayedLoadMoreZigs = _.debounce(loadMoreZigs, 100); // Adjust delay as needed

$(document).ready(function () {
    $(window).resize(function () {
        var bodyheight = ($(this).height()) * 0.9;
        $("#sidebar").height(bodyheight);
    }).resize();

});

$(document).ready(function() {
// $('#src_run').click(function() {
    var inputElement = document.getElementById('src_value');
    inputElement.addEventListener('input', function() {
    var formFunction='search_friends'
    var src_value=document.getElementById('src_value').value
    var suggestion_area=document.querySelector('.search_suggestions')
    var csrftoken = getCookie('csrftoken');
    // Create the data object to send in the AJAX request
    var data = {
        'src_value': src_value,
        'form_function': formFunction
    };

    // Send the AJAX request to your Django view
    $.ajax({
        headers: {
                'X-CSRFToken': csrftoken  // Include the CSRF token in the request headers
            },
        url: '/',
        method: 'POST',
        data: data,
        success: function(response) {
            // Handle the response from the Django view
            // console.log(response);

            var search_results=[]
            if(response!=''){
                suggestion_area.innerHTML = "<hr>";
                response.forEach(function(matched_users_data) {
                    // search_results.append(matched_users_data.username)
                    search_results.push(matched_users_data.userID)
                });
            
                search_results.forEach(function(item) {
                    var li = document.createElement("li");
                    var iconSpan = document.createElement("span");
                    var a = document.createElement("a");
                    iconSpan.className = "material-symbols-outlined textuniversal";
                    iconSpan.style.verticalAlign = "middle";
                    iconSpan.textContent = "account_circle";
                    a.textContent = item;
                    // li.innerHTML = iconSpan+ "<a>" +a+  "</a>";
                    

                    // Append the icon and the link to the li element
                    a.style.paddingLeft='3px'
                    li.appendChild(iconSpan);
                    li.append(a)
                    suggestion_area.appendChild(li);
                });
            }
            else{
                suggestion_area.innerHTML = "";
            }
        },
        error: function(xhr, textStatus, error) {
            console.log(xhr.statusText);
        }
    });
});
});

$(document).ready(function() {
$('.add_friend').click(function() {
    var formFunction='add_friends'
    var selected_user = $(this).attr('selected-user');
    var csrftoken = getCookie('csrftoken'); 
    console.log(selected_user)
    // Creating the data object to send in the AJAX request
    var data = {
        'selected_user': selected_user,
        'form_function':formFunction
    };

    // Sending the AJAX request to your Django view
    $.ajax({
        headers: {
                'X-CSRFToken': csrftoken  // Include the CSRF token in the request headers
            },
        url: '/',
        method: 'POST',
        data: data,
        success: function(response) {
            console.log(response);
        },
        error: function(xhr, textStatus, error) {
            console.log(xhr.statusText);
        }
    });
});
});
function generateReplyHtml(replydata){
var reply_content=replydata.content;
var replier_identity=replydata.sender;
console.log(reply_content+'hh')
replyHtml=''
replyHtml+=`
<li style="margin-bottom: 1vh;" >
    <div style="display: flex;justify-content: space-between;">
        <div>
            <span class="material-symbols-outlined textuniversal"
                style="vertical-align: middle;">account_circle</span>
            <span style="vertical-align: middle;overflow: none;font-family: 'Open Sans';">
                <span class="replier_identity">Anonymous: </span><span>${reply_content}</span>
            </span> 
        </div>
        <div>
            <!-- <span class="material-symbols-outlined">flag</span> -->
            <span class="material-symbols-outlined"style='padding-left: 20px;'>thumb_up</span>
        </div>
    </div>
</li>
`
return replyHtml;
}

$('.sbs').on('click', '.add_reply', function()  {
    var formFunction = $(this).attr('formFunction');
    var currentZig= $(this).attr('currentZig');
    var opinion_box=document.querySelector('#opinion_box_'+currentZig);
    var opinion=opinion_box.value;
    var replySection=document.querySelector('#reply-section_'+currentZig);
    
    var csrftoken = getCookie('csrftoken'); 
    var data = {
        'form_function': formFunction,
        'current_zig':currentZig,
        'opinion':opinion
    };

    $.ajax({
        headers: {
            'X-CSRFToken': csrftoken 
        },
        url: '/',
        method: 'POST',
        data: data,
        success: function(response) {
            
            if(response!=''){
            var reply_html = generateReplyHtml(response);
            $('#reply-section_'+currentZig).prepend(reply_html);
            opinion_box.value=''
            replySection.scrollTop(0);
            }
        },
        error: function(xhr, textStatus, error) {
            console.log(xhr.statusText);
        }
    });
});

function generateZigHtml(zigData) {
console.log(zigData.id)
var username = zigData.user.userdata.Username;
var profilePicUrl = zigData.user.userdata.profilePic;
var userID = zigData.user.userdata.userID;
var title = zigData.title;

var replyHtml = '';


if (zigData.replies && zigData.replies.length > 0) {
    // replyHtml += '<ul style="list-style-type:none;height: 20vh;width: 90%;overflow-y: scroll;margin:0;padding: 0;padding-left: 10px;padding-right:5%;" class="textuniversal2" id="reply-section">';
    zigData.replies.forEach(function(reply) {
        if(reply.sender==reply.current_user){
        replyHtml += `
            <li style="margin-bottom: 1vh;">
                <div style="display: flex;justify-content: space-between;">
                    <div>
                        <span class="material-symbols-outlined textuniversal" style="vertical-align: middle;">account_circle</span>
                        <span style="vertical-align: middle;overflow: none;font-family: 'Open Sans';">
                        <span class="replier_identity">You: </span><span>${reply.content}</span>
                        </span>
                    </div>
                    <div>
                        <span class="material-symbols-outlined"style='padding-left: 20px;'>thumb_up</span>
                    </div>
                </div>
            </li>
        `;
        }
    });
    zigData.replies.forEach(function(reply) {
        if(reply.sender!=reply.current_user){
        replyHtml += `
            <li style="margin-bottom: 1vh;">
                <div style="display: flex;justify-content: space-between;">
                    <div>
                        <span class="material-symbols-outlined textuniversal" style="vertical-align: middle;">account_circle</span>
                        <span style="vertical-align: middle;overflow: none;font-family: 'Open Sans';">
                        <span class="replier_identity">Anonymous: </span><span>${reply.content}</span>
                        </span>
                    </div>
                    <div>
                        <span class="material-symbols-outlined"style='padding-left: 20px;'>thumb_up</span>
                    </div>
                </div>
            </li>
        `;
        }
    });
    // replyHtml += '</ul>';
}

var zigHtml = `
    <center>
        <div class="card" style="width:75%;text-align: justify;padding: 1vh;overflow: hidden;margin-bottom: 18px;">
            <div class="container">
                <center>
                    <div class="material-symbols-outlined" style="font-size:10vw;vertical-align: middle;background-image: url(${profilePicUrl});background-position: center;width:112.91px;height: 112.91px;background-size:contain;background-repeat: no-repeat;"></div>
                    <div style="color:gray;font-family: 'Open Sans', sans-serif;font-size: 1em;">${userID}</div>
                    <div class="title_font" style="font-family: 'Open Sans', sans-serif;">${title}</div>
                </center>
                <br>

                <!-- Replies section -->
                <ul style="list-style-type:none;height: 20vh;width: 90%;overflow-y: scroll;margin:0;padding: 0;padding-left: 10px;padding-right:5%;" class="textuniversal2 reply_section_class" id='reply-section_${zigData.id}'>
                ${replyHtml}
                </ul>
                <!-- Opinion wrapper -->
                <center>
                <div class="opiwrapper" style="margin-bottom:3vh;">
                    <input id="opinion_box_${zigData.id}" class="opiinputbutton" type="text" placeholder="What's your opinion?" />
                    <button formFunction="user_opinion" currentZig="${zigData.id}" class="opi add_reply">
                        <span class="material-symbols-outlined">share</span>
                    </button>
                </div>
                </center>
            </div>
        </div>
    </center>
`;

return zigHtml;
}


function loadMoreZigs() {
// Making an AJAX request to the server to fetch the next page of zigs
var formFunction= 'load_zigs';
var csrftoken = getCookie('csrftoken'); 
console.log(currentPage)

$.ajax({
headers: {
            'X-CSRFToken': csrftoken  // Include the CSRF token in the request headers
        },
url: '/', 
method: 'POST',
data: {
    page: currentPage,
    items_per_page: itemsPerPage,
    form_function:formFunction
},
success: function(response) {
    // Generate and append new zigs
    if(response!=''){
        
        response.forEach(function(zigData) {
            var zigHtml = generateZigHtml(zigData);
            $('.sbs').append(zigHtml);
        });
        currentPage++;
    }
},
error: function(xhr, textStatus, error) {
    console.log(xhr.statusText);
}
});
}



function getCookie(name) {
var cookieValue = null;
if (document.cookie && document.cookie !== '') {
    var cookies = document.cookie.split(';');
    for (var i = 0; i < cookies.length; i++) {
    var cookie = cookies[i].trim();
    if (cookie.substring(0, name.length + 1) === (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
    }
    }
}
return cookieValue;
}

// myzigs page

