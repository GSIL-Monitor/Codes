package com.tsb.web.controller;

import java.util.HashMap;
import java.util.Map;

import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestMethod;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.ResponseBody;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.tsb.dao.read.user.UserReadDao;
import com.tsb.model.user.User;
import com.tsb.util.CookieManager;


@Controller
@RequestMapping(value = "/api/user/access")
@SuppressWarnings(value = { "rawtypes", "unchecked" })
public class AccessCtrl extends BaseController{

	@Autowired
	private UserReadDao userReadDao;
	
	@RequestMapping(value = "/identify", method=RequestMethod.POST)
	@ResponseBody
	public Map identify(HttpServletRequest request,
						HttpServletResponse response,
						@RequestParam("path") String path,
						@RequestBody String jsonRequest){
		
		String ip = request.getHeader("X-Forwarded-For");
		if (ip == null || "".equals(ip.trim())) {
			ip = request.getHeader("X-Real-IP");
		}
		User user = null;
		
		CookieManager cookieManager = new CookieManager(request, response);
		String strUserid = cookieManager.getCookieValue("userid");
		if( strUserid != null && !"".equals(strUserid) ){
        	int userid = 0;
        	try{
        		userid = Integer.parseInt(strUserid);
        	}
        	catch(Exception e){
        	}
        	if( userid > 0){
        		User _user = userReadDao.getById(userid);
    			if( _user != null && (_user.getActive()=='Y' || _user.getActive()==null)){
	        		String token = cookieManager.getCookieValue("token");
	        		if( token != null && !"".equals(token)){
        				if(token.equals(_user.getToken())){
        					user = _user;
        				}
	        		}
	        		if(user == null){
	        			String keeploginsecret = cookieManager.getCookieValue("keeploginsecret");
	        			if( keeploginsecret != null && !"".equals(keeploginsecret)){
	        				if(keeploginsecret.equals(_user.getKeepLoginSecret())){
	        					user = _user;
	        				}
	        			}
	        		}
    			}
        	}
		}
        
		String json_post_body = "";
		try{
			ObjectMapper mapper = new ObjectMapper();
			Map<String, Object> data = (Map<String, Object>) mapper.readValue(jsonRequest, Map.class);
			if( user == null){
				data.put("userid", -1);
			}
			else{
				data.put("userid", user.getId());
			}
			data.put("ip", ip);
			json_post_body = mapper.writeValueAsString(data);
		}
		catch(Exception e) {
			e.printStackTrace();
		}
		System.out.println(json_post_body);
		
		response.setHeader("X-Accel-Redirect",path);
		try{
			response.setHeader("postbody", new String(json_post_body.getBytes(), "ISO-8859-1"));
		}
		catch(Exception e){
			e.printStackTrace();
		}
				  
		Map map = new HashMap();
		map.put("code", 0);
		return map;
	}
	
}
