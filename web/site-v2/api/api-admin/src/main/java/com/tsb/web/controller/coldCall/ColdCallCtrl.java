package com.tsb.web.controller.coldCall;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestMethod;
import org.springframework.web.bind.annotation.ResponseBody;

import com.tsb.admin.service.ColdCallService;
import com.tsb.admin.vo.ColdCallVO;
import com.tsb.util.RequestVO;
import com.tsb.web.controller.BaseController;

@Controller
@RequestMapping(value = "/api/admin/coldCall")
@SuppressWarnings({ "rawtypes", "unchecked" })
public class ColdCallCtrl extends BaseController {
	@Autowired
	private ColdCallService coldCallService;

	@RequestMapping(value = "/count", method = RequestMethod.POST)
	@ResponseBody
	public Map countAllColdCall(@RequestBody RequestVO request) {
		Map map = new HashMap();
		map.put("total", coldCallService.totalColdCall());
		map.put("matched", coldCallService.coutMatchedColdCall());
		map.put("unmatched", coldCallService.coutUnmatchedColdCall());
		map.put("code", 0);
		return map;
	}

	@RequestMapping(value = "/unmatch", method = RequestMethod.POST)
	@ResponseBody
	public Map unmatchList(@RequestBody RequestVO request) {

		Integer from = (Integer) request.getPayload().get("from");
		Integer pageSize = (Integer) request.getPayload().get("pageSize");
		List<ColdCallVO> list = coldCallService.getUnmatchedList(from, pageSize);
		Map map = new HashMap();
		map.put("list", list);
		map.put("code", 0);
		return map;
	}
	@RequestMapping(value = "/match", method = RequestMethod.POST)
	@ResponseBody
	public Map matchedList(@RequestBody RequestVO request) {

		Integer from = (Integer) request.getPayload().get("from");
		Integer pageSize = (Integer) request.getPayload().get("pageSize");
		List<ColdCallVO> list = coldCallService.getmatchedList(from, pageSize);
		Map map = new HashMap();
		map.put("list", list);
		map.put("code", 0);
		return map;
	}

}
