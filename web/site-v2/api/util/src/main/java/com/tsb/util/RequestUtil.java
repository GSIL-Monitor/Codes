package com.tsb.util;

import com.fasterxml.jackson.databind.ObjectMapper;

public class RequestUtil {
	public RequestVO transform(String request){
		
		RequestVO req  = new RequestVO();
		try{
			ObjectMapper mapper = new ObjectMapper();
			req = mapper.readValue(request, RequestVO.class);
		}
		catch(Exception e) {
			e.printStackTrace();
		}
		
		
		return req;
	}
	
	public boolean requireLogin(Integer userId){
		if(userId <=0)
			return false;
		
		return true;
	}
	
}
