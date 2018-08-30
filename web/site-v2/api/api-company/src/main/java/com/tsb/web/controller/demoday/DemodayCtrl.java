package com.tsb.web.controller.demoday;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestMethod;
import org.springframework.web.bind.annotation.ResponseBody;

import com.tsb.company.service.CompanyService;
import com.tsb.company.service.DemodayService;
import com.tsb.company.vo.DemodayPreScoreVO;
import com.tsb.company.vo.DemodayVO;
import com.tsb.util.RequestVO;
import com.tsb.web.controller.BaseController;

@Controller
@RequestMapping(value = "/api/company/demoday")
@SuppressWarnings(value = { "rawtypes", "unchecked" })
public class DemodayCtrl extends BaseController {
	@Autowired
	private DemodayService demodayService;

	@Autowired
	private CompanyService companyService;

	@RequestMapping(value = "/get", method = RequestMethod.POST)
	@ResponseBody
	public Map getDemoday(@RequestBody RequestVO request) {
		Integer demodayId = (Integer) request.getPayload().get("demodayId");
		DemodayVO demodayVO = demodayService.getDemoday(demodayId);
		Map map = new HashMap();
		map.put("demoday", demodayVO);
		map.put("code", 0);
		return map;
	}

	@RequestMapping(value = "/list", method = RequestMethod.POST)
	@ResponseBody
	public Map getDemodayList(@RequestBody RequestVO request) {
		List<DemodayVO> demodayVOList = demodayService.get();
		Map map = new HashMap();
		map.put("list", demodayVOList);
		map.put("code", 0);
		return map;
	}

	@RequestMapping(value = "/nav", method = RequestMethod.POST)
	@ResponseBody
	public Map getDemodayNav(@RequestBody RequestVO request) {
		Integer demodayId = (Integer) request.getPayload().get("demodayId");
		String code = (String) request.getPayload().get("code");
		DemodayVO demodayVO = demodayService.getDemoday(demodayId);
		Map map = new HashMap();
		map.put("demoday", demodayVO);
		map.put("companyName", code == null ? null : companyService.getName(code));
		map.put("code", 0);
		return map;
	}
	
	@RequestMapping(value = "/notPassedList", method = RequestMethod.POST)
	@ResponseBody
	public Map getNotPassedList(@RequestBody RequestVO request) {
		Integer userId = request.getUserid();
		Integer demodayId = (Integer) request.getPayload().get("demodayId");
		Integer start = (Integer) request.getPayload().get("start");
		Integer pageSize =20;
		List<DemodayPreScoreVO> notPassedList = demodayService.notPassedList(start,pageSize,userId, demodayId);
		int total = demodayService.countNotPassNum(demodayId);
		Map map = new HashMap();
		map.put("code", 0);
		map.put("list", notPassedList);
		map.put("total", total);
		return map;
	}

}
