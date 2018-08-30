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

import com.tsb.company.service.SectorService;
import com.tsb.model.company.Sector;
import com.tsb.util.RequestVO;

@Controller
@RequestMapping(value = "/api/company/sector")
@SuppressWarnings({ "rawtypes", "unchecked" })
public class SectorCtrl extends BaseController {
	@Autowired
	private SectorService sectorService;

	@RequestMapping(value = "/list", method = RequestMethod.POST)
	@ResponseBody
	public Map getSectors(@RequestBody RequestVO request) {
		
		List sectors = sectorService.get();
		Map map = new HashMap();
		map.put("sectors", sectors);
		map.put("code", 0);
		return map;

	}
	
	@RequestMapping(value = "/second", method = RequestMethod.POST)
	@ResponseBody
	public Map getSecondSectors(@RequestBody RequestVO request) {
		int id = (int) request.getPayload().get("id");
		List sectors = sectorService.get(id);
		Map map = new HashMap();
		map.put("sectors", sectors);
		map.put("code", 0);
		return map;

	}
	
	@RequestMapping(value = "/update", method = RequestMethod.POST)
	@ResponseBody
	public Map updateCompanySector(@RequestBody RequestVO request) {
		List sectorIds = (List) request.getPayload().get("sectorIds");
		Integer companyId = (Integer) request.getPayload().get("companyId");
		Integer userId = request.getUserid();
		
		sectorService.updateCompanySector(sectorIds, companyId, userId);
		Map map = new HashMap();
		map.put("code", 0);
		return map;

	}
	
	@RequestMapping(value = "/update/one", method = RequestMethod.POST)
	@ResponseBody
	public Map updateSector(@RequestBody RequestVO request) {
		Integer companyId = (Integer) request.getPayload().get("companyId");
		Integer sectorId = (Integer) request.getPayload().get("sectorId");
		Integer oldId = (Integer) request.getPayload().get("oldId");
		Integer userId = request.getUserid();
		
		Sector sector =  sectorService.updateSector(companyId, sectorId, oldId, userId);
		Map map = new HashMap();
		map.put("code", 0);
		map.put("sector", sector);
		return map;

	}
	

}
