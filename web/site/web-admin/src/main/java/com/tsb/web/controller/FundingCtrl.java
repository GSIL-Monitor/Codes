package com.tsb.web.controller;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestMethod;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.ResponseBody;

import com.tsb.admin.service.FundingService;
import com.tsb.admin.vo.FundingInvestorVO;
import com.tsb.admin.vo.FundingVO;
import com.tsb.admin.vo.IDVO;
import com.tsb.admin.vo.SourceFundingVO;
import com.tsb.model.Funding;
import com.tsb.model.FundingInvestorRel;

@Controller
@RequestMapping(value = "/api/admin/funding")
@SuppressWarnings(value = { "rawtypes", "unchecked" })
public class FundingCtrl {

	@Autowired
	private FundingService fundingService;
	
	@RequestMapping(value = "/get")
	@ResponseBody
	public List getFundingById(@RequestParam("id") Integer id) {

		return fundingService.get(id);
	}
	
	@RequestMapping(value = "/get/all")
	@ResponseBody
	public List getFundingVOByCompanyId(@RequestParam("id") Integer id) {

		return fundingService.getFundingVO(id);
	}
	

	@RequestMapping(value = "/get/vo")
	@ResponseBody
	public List getFundingVOById(@RequestParam("id") Integer id) {
		
		return fundingService.getFundingVO(id);
	}
	
//	@RequestMapping(value = "/source/get/all")
//	@ResponseBody
//	public List getSourceByCompanyId(@RequestParam("id") Integer id) {
//
////		return fundingService.getSource(id);
//	}
	
	@RequestMapping(value = "/source/get")
	@ResponseBody
	public List getSourceByFundingId(@RequestParam("id") Integer id) {

		return fundingService.getSourceFunding(id);
	}
	
	@RequestMapping(value = "/investor/source/get")
	@ResponseBody
	public List getSourceFundingInvestorByfirId(@RequestParam("id") Integer id) {

		return fundingService.getSourceInvestorRel(id);
	}
	
	@RequestMapping(value = "/add", method={RequestMethod.PUT})
	@ResponseBody
	public Object addFunding(@RequestBody Funding funding) {
		Integer id = fundingService.add(funding);
		IDVO idVO = new IDVO();
		idVO.setId(id);
		
		return idVO;
	}
	
	@RequestMapping(value = "/update", method={RequestMethod.PUT})
	@ResponseBody
	public String updateFunding(@RequestBody Funding funding) {
		fundingService.update(funding);
		
		return "{'code':0}";
	}
	
	@RequestMapping(value = "/delete", method={RequestMethod.PUT})
	@ResponseBody
	public String deleteFunding(@RequestBody Funding funding) {
		fundingService.delete(funding);
		
		return "{'code':0}";
	}
	
	@RequestMapping(value = "/investor/add", method={RequestMethod.PUT})
	@ResponseBody
	public Object addFundingInvestorRel(@RequestBody FundingInvestorRel fir) {
		FundingInvestorVO fiVO = fundingService.addFIR(fir);
		
		return fiVO;
	}
	
	@RequestMapping(value = "/investor/update", method={RequestMethod.PUT})
	@ResponseBody
	public String updateFundingInvestorRel(@RequestBody FundingInvestorRel fir) {
		fundingService.updateFIR(fir);
		
		return "{'code':0}";
	}
	
	@RequestMapping(value = "/investor/delete", method={RequestMethod.PUT})
	@ResponseBody
	public String deleteFundingInvestorRel(@RequestBody FundingInvestorRel fir) {
		fundingService.deleteFIR(fir);
		
		return "{'code':0}";
	}
	
	
}
