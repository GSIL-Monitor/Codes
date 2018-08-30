package com.tsb.web.controller.demoday;

import java.util.HashMap;
import java.util.Map;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestMethod;
import org.springframework.web.bind.annotation.ResponseBody;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.tsb.company.service.DemodayService;
import com.tsb.model.demoday.DemodayCompany;
import com.tsb.util.RequestVO;
import com.tsb.web.controller.BaseController;

@Controller
@RequestMapping(value = "/api/company/demoday/company")
@SuppressWarnings(value = { "rawtypes", "unchecked" })
public class DemodayCompanyCtrl extends BaseController {
	@Autowired
	private DemodayService demodayService;
	
	@RequestMapping(value = "/get", method = RequestMethod.POST)
	@ResponseBody
	public Map getDemodayCompany(@RequestBody RequestVO request) {
		Integer userId = request.getUserid();
		Integer demodayId = (Integer) request.getPayload().get("demodayId");
		Integer  companyId = (Integer) request.getPayload().get("companyId");
		Map result = demodayService.getDemodayCompany(demodayId, companyId, userId);
		Map map = new HashMap();
		map.put("demodayCompany", result.get("demodayCompany"));
		map.put("commitOrg", result.get("commitOrg"));
		map.put("code", 0);
		return map;
	}

	@RequestMapping(value = "/update", method = RequestMethod.POST)
	@ResponseBody
	public Map updateDemodayCompany(@RequestBody RequestVO request) throws Exception {
		//Integer userId = request.getUserid();
		ObjectMapper mapper = new ObjectMapper();
		String str = mapper.writeValueAsString(request.getPayload().get("demodayCompany"));
		DemodayCompany demodayCompany = mapper.readValue(str, DemodayCompany.class);
		demodayService.updateDemodayCompany(demodayCompany);
		Map map = new HashMap();
		map.put("code", 0);
		return map;
	}

	@RequestMapping(value = "/add", method = RequestMethod.POST)
	@ResponseBody
	public Map addDemodayCompany(@RequestBody RequestVO request) {
		Integer userId = request.getUserid();
		Integer demodayId = (Integer) request.getPayload().get("demodayId");
		String code = (String) request.getPayload().get("code");
		Integer result = demodayService.addDemodayCompany(demodayId, code, userId);
		Map map = new HashMap();
		// result是－1表示已经提交过项目，为0表示成功
		map.put("result", result);
		map.put("code", 0);
		return map;
	}

	@RequestMapping(value = "/commit", method = RequestMethod.POST)
	@ResponseBody
	public Map commitDemodayCompany(@RequestBody RequestVO request) throws Exception {
		Integer userId = request.getUserid();
		ObjectMapper mapper = new ObjectMapper();
		String demodayCompnyStr = mapper.writeValueAsString(request.getPayload().get("demodayCompny"));
		DemodayCompany demodayCompany = mapper.readValue(demodayCompnyStr, DemodayCompany.class);
		Integer result = demodayService.commitDemodayCompany(demodayCompany,userId);
		Map map = new HashMap();
		// result是－1表示已经提交过项目，为0表示成功
		map.put("result", result);
		map.put("code", 0);
		return map;
	}

}
