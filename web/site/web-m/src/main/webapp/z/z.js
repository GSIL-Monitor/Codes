$(function(){

    //$(".fakeloader").fakeLoader({
    //            bgColor:"#6aa0d1",
    //            spinner:"spinner7"
    //});



	$(window).on("load resize scroll", function() {
		fix_window();
	});

	//$('.load-failed').click(function(){
    //
	//})

	var contain_width = $('.page-wrap').width();
	var contain_height = $('.page-wrap').height();

	//setInterval("upArrow()", 1000);

	var url = window.location.href;
	var code = url.split("?")[1];
	code = code.split("#")[0];

	$.ajax({
		  type: 'GET',
		  url: './api/m/c/overview?code='+code,
		  dataType: 'json',
		  timeout: 3000,
		  context: $('body'),
		  success: function(data){
			  c = data.company;
			  title = c.productName + '—众筹分析报告';
			  document.title = title;
			  $('.doc-name').html('众筹分析报告');

			  console.log(data)
			  //page1
			  $(".c-name").html(c.productName);
			  $('.c-desc').append(c.brief);


			  //page2 desc
			  $('.c-fullName').html(c.companyFullName);
			  $('.c-stage').html(c.stage);
			  $('.c-loc').html(c.location);
			  $('.c-founded').html(c.establishDate.slice(0,7));

			  $.each(c.tagRelList, function(index, item){
				  var tag = '<div class="label">'+item.tagName+'</div>';

				  $('.c-tag').append(tag);
			  })

			  //page3 funding footprint

			  var footprints = data.company.footprintList.reverse();
			  var foot_date, foot_desc, foot_div;
			  $.each(footprints, function(index, item){
				  foot_date = '<div class="time-info">'+item.footDate.slice(0,7)+'</div>';
				  foot_desc = '<div class="develop-info">'+item.footDesc+'</div>';
				  foot_div = '<div class="develop-div">'+foot_date+foot_desc+'</div>';

				  $('.develop-detail').append(foot_div);
			  });


			  var fundings = data.company.funding;

			  var funding_div;
			  $.each(fundings, function(index, item){
				  funding_div = parseFunding(item, "funding");

				  $('.develop-detail').append(funding_div);
                  $('.basic-content').css('width', contain_width-90+'px');
				  $('.develop-info').css('width', contain_width-160+'px');
			  });


			  //comps
			  var comps = c.relCompanies;
		      var comps_name,
			 	  comps_desc,
				  comps_basic,
				  comps_date,
				  comps_fundings,
				  comps_div;

			  var name_len, name_type, name, c_len, e_len;

			  $.each(comps, function(index, item){
				  if (index < 5){

					  name = item.productName;
					  name_len = item.productName.length;
					  c_len = strlen(name);
					  e_len = name_len*2 - c_len;

					  if (name_len ==2){
					  	name_type = "name2";
					  }
					  else if (name_len == 3)
					  	name_type = "name3";
					  else if (name_len == 4){
					  	 name_type = "name4";
						  name = item.productName.slice(0,2)+'</br>'+item.productName.slice(2,4);
					  }
					  else
					  	name_type = "";

					  name_type += " name-a"+c_len;

					  comps_name ='<div class="basic-header member-name"><div class="header-c '+name_type+'">'+
						  name+'</div></div>';

					  if (item.brief != null)
					  	comps_desc = '<p class="comps-desc">'+item.brief+'</p>';
					  else
						  comps_desc = '';

					  if (item.establishDate != null)
					  	  comps_date = item.establishDate.slice(0,7);
					  else
						  comps_date = '';
					  comps_basic = '<div class="develop-div"><span class="time-info-s">'+comps_date+
						  			'</span>成立于'+item.location+'</div>';

					  comps_fundings = '';
					  $.each(item.funding, function(index, item){
						  funding_div = parseFunding(item, "comps-funding");
						  comps_fundings += funding_div;
					  });

					  comps_fundings = '<div>'+comps_fundings+'</div>';
					  comps_div = '<div class="basic-info">'+
						  				comps_name +
						  			'<div class="basic-content comps-detail">'+comps_desc+comps_basic+comps_fundings+
						  			'</div>'+
					  				'</div>';

					  $('.comps').append(comps_div);
					  $('.basic-content').css('width', contain_width-90+'px');
					  $('.develop-info').css('width', contain_width-160+'px');
				  }
			  });

			  //$(".fakeloader").fadeOut(600, function(){
				  $('.page-wrap').fadeIn(500);
				  $('.swiper-container').show();
			  //});


		  },
		  error: function(xhr, type){
			  //alert('error')
			  $('.load-failed').show();
			  $('.load-failed').html('请求超时，请刷新页面');
		  }
		})

	$.ajax({
		  type: 'GET',
		  url: './api/m/c/team?code='+code,
		  dataType: 'json',
		  timeout: 3000,
		  context: $('body'),
		  success: function(data){
			  var team = data.team;
			  var jobs = data.jobs;
			  var recruit = data.recruit;

			  var mem_name;
			  var mem_position='';
			  var mem_joinDate='';
			  var mem_edu='';
			  var mem_work='';
			  var mem_div;

			  var name_len;

			  $.each(team, function(index, item){
				  name_len = item.member.memberName.length;
				  if (name_len == 2)
					  mem_name ='<div class="basic-header member-name"><div class="header-c name2">'+
								item.member.memberName+'</div></div>';
				  else if (name_len ==3)
					  mem_name ='<div class="basic-header member-name"><div class="header-c name3">'+
						  item.member.memberName+'</div></div>';

				  if (item.memberPosition != "")
					mem_position = '<p class="member-position">'+item.memberPosition+'</p>';

				  if (item.joinDate != "" && item.joinDate != null)
					mem_joinDate = '<p>'+item.joinDate+'</p>';

				  //mem_edu = '<p>'+item.member.educationExperience+'</p>';
				  mem_work = '<p>'+item.member.workExperience+'</p>';
				  mem_div = mem_name+'<div class="basic-content member">'+
								mem_position+mem_work+
							'</div>';

				  $('.team').append(mem_div);

			  });


			  var job = '';
			  var num = (contain_height/1.2-320)/40;
			  num = Math.round(num)*2;

			  $.each(jobs, function(index, item) {
				  job = '<div class="item">' +
					  '<span class="vline"></span>' +
					  '<span class="spot"></span>' +
					  '<span class="info">' +
					  '<p class="phase">' +
					  item.positionName +
					  '</p>' +
					  '<p class="time">' +
					  item.bornTime.slice(0, 10) +
					  '</p></span></div>';

					 $('.jobs').append(job);

			  })
		  }
	});

	$.ajax({
		  type: 'GET',
		  url: '/api/news/getByCompany?code='+code+'&page=1',
		  dataType: 'json',
		  timeout: 3000,
		  context: $('body'),
		  success: function(data){
			  var newsList = data.result;
			  $('#report-num').text(newsList.length);
			  var news;
			  $.each(newsList, function(index, item){
				  news =  '<li class="tl-node">'+
							  '<p class="tl-title"><a href="'+item.news.newsUrl+'" target="_blank">'+
							  item.news.newsTitle+
							  '</a></p><br/>'+
					  		'<p class="tl-stamp"><span>'+
							  item.news.newsDate.slice(5,10)+
							  '</span><span class="tl-website">'+item.news.title+'</span>'+
							  '</p></li>';

				  $('.news-list').append(news);

			  })

		  }
	});

	$.ajax({
		type: 'GET',
		url: '/api/mobile/get?code='+code,
		dataType: 'json',
		timeout: 3000,
		context: $('body'),
		success: function(data){
			var m = data.result;
			$('.recurit').html(m.recruitSummary);
			$('.recurit-location').html(m.recruitDistribution);

			$('#android-download').html(m.androidDownload);
			$('#android-distribute').html(m.androidDistribution);
			
			$('#ios-comment-num').html(m.iosComment);
			$('#ios-summary').html(m.iosCommentSummary);
			
			$('#business-data').html(m.businessData);

			$('#report-summary').html(m.reportSummary);
			$('#report-focus').html(m.reportFocus);


			//var product_pic = '<img src="/file/'+m.androidPic+'/product.png" />';
			//$('.product-pic').html(product_pic);

		}
	})



	$.ajax({
		type: 'GET',
		url: '/api/mobile/pic/get?code=' + code,
		dataType: 'json',
		timeout: 3000,
		context: $('body'),
		success: function (data) {
			var pics = data.result;

			$.each(pics, function(index, item){
				var product_pic = '<div class="swiper-slide"><img src="/file/'+item.pic+'/product.png" /></div>';
				$('.swiper-wrapper').append(product_pic);
			});
			var swiper = new Swiper('.swiper-container', {
			    pagination: '.swiper-pagination',
			    paginationClickable: '.swiper-pagination'
			});

		}

	})

});




function fix_window(){
	var contain_width = $('.page-wrap').width();
	$('.basic-content').css('width', contain_width-90+'px');
	$('.c-c').css('width', contain_width-160+'px');
	$('.develop-info').css('width', contain_width-160+'px');

}


function digitReg(s){
	var pattern = '^[A-Za-z0-9]+$';
 	console.log(pattern.match(s))
}

function strlen(str){
    var len = 0;
    for (var i=0; i<str.length; i++) { 
     var c = str.charCodeAt(i); 
     if ((c >= 0x0001 && c <= 0x007e) || (0xff60<=c && c<=0xff9f)) { 
       len++; 
     } 
     else { 
      len+=2; 
     } 
    } 
    return len;
}

function parseFunding(item, type){
	var funding_desc, funding_date, funding_currency,
		funding_amout, funding_investors,
		investor, funding_round, funding_div;

		funding_currency = item.fundingCurrency;
	if (funding_currency == 501)
		funding_currency = '美元';
	else if (funding_currency == 502)
		funding_currency = '人民币';
	else
		funding_currency = '';

	funding_amout = item.fundingInvestment.replace('k','千').replace('m','百万').replace('b','亿');
	funding_amout = funding_amout.replace('0千','万');
	funding_amout = funding_amout.replace('0万','十万');
	funding_amout = funding_amout.replace('0百','千');
	funding_amout = funding_amout.replace('0千万','亿');

	var precise = item.fundingInvestmentPrecise
	if (!precise && funding_amout == '0'){
		funding_amout = '额未披露';
		funding_currency = '';
	}else if (!precise){
		funding_amout = '数'+funding_amout.substring(1);
	}


	funding_desc = '<span class="funding-desc">'+
		'融资'+
		funding_amout+funding_currency+
		'，</span>';


	funding_investors = '';
	$.each(item.investorList, function(index, item){
		if (item.investor == null)
			investor = '<span>未披露</span>';
		else
			investor = '<span class="investor-span">'+item.investor.investorName+'</span>';
		funding_investors += investor;
	});


	if (type == 'funding')
		funding_date = '<div class="time-info">'+item.fundingDate.slice(0,7)+'</div>';
	else
		funding_date = '<div class="time-info-s">'+item.fundingDate.slice(0,7)+'</div>';

	funding_investors = '<div class="funding-investor">投资方:&nbsp;&nbsp;' + funding_investors + '</div>';
	funding_div = '<div class="develop-div">'+funding_date+
					'<div class="develop-info">'+funding_desc+funding_investors+
					'</div></div>';


	return funding_div;
}
