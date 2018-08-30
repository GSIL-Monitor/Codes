package com.tsb.web.controller;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestMethod;
import org.springframework.web.bind.annotation.ResponseBody;

import com.tsb.company.service.JobService;
import com.tsb.util.RequestVO;

@Controller
@RequestMapping(value = "/api/company/job")
@SuppressWarnings({ "rawtypes", "unchecked" })
public class JobCtrl extends BaseController {
	@Autowired
	private JobService jobService;

	@RequestMapping(value = "/list", method = RequestMethod.POST)
	@ResponseBody
	public Map getJobs(@RequestBody RequestVO request) {
		int id = (int) request.getPayload().get("id");
		List jobList = jobService.getJobs(id);
		Map map = new HashMap();
		map.put("jobs", jobList);
		map.put("code", 0);
		return map;

	}
}
