function likebuttonclick(x,reply_id) {
	if (x.classList.contains("liked")) { x.classList.remove("liked");
	likebutton=x.getElementsByTagName("span"); 

	likebutton[1].classList.remove("likeflipper"); }
	else { x.classList.add("liked");

	likebutton=x.getElementsByTagName("span"); 

	likebutton[1].classList.add("likeflipper");;
	
	// UIkit.notification("<span uk-icon='icon: check'></span>Liked", { pos: 'bottom-center' }) ;

	}


	var id=reply_id
	
	var csrftoken = getCookie('csrftoken'); 
	var data = {
		'form_function': 'liked',
		'reply_id':id,

	};
	console.log('liked')
	$.ajax({
		headers: {
			'X-CSRFToken': csrftoken 
		},
		url: "/",
		method: 'POST',
		data: data,
		success: function(response) {
			like_count=parseInt(document.querySelector('.like_count_'+reply_id).innerHTML)
			if(response=='liked'){
				like_count=like_count+1
			}
			else{
				like_count=like_count-1
			}
			document.querySelector('.like_count_'+reply_id).innerHTML=String(like_count)
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
