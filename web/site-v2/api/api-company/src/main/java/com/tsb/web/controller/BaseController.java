package com.tsb.web.controller;

import java.util.HashMap;
import java.util.Map;

import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.ResponseBody;

public class BaseController {
	
	@SuppressWarnings({ "rawtypes", "unchecked" })
	@ExceptionHandler(Throwable.class)
	@ResponseBody
	public Object handleIOException(Exception ex) {
		ex.printStackTrace();
		Map map = new HashMap();
		map.put("code", -1);
		return map;
	}


}
