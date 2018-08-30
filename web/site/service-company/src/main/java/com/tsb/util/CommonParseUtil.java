package com.tsb.util;

import java.io.Console;
import java.util.ArrayList;
import java.util.List;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

import org.springframework.stereotype.Component;

import com.tsb.model.Funding;


@Component
public class CommonParseUtil {
	
//	public List<CompanyTagRel> filterTag(List<CompanyTagRel> tagList){
//		List<CompanyTagRel> newTags = new ArrayList<CompanyTagRel>();
//		for(CompanyTagRel ctr : tagList){
//			if(ctr.getTagId() != 0)
//				newTags.add(ctr);
//		}
//		return newTags;
//	}
	
//	public List<Funding> parseFundings(List<Funding> fundings){
//		List<Funding> result  = new ArrayList<Funding>();
//		for(Funding f: fundings){
//			
//			String invset = String.valueOf(f.getInvestment());
//			Integer investment =parseFinance(invset).;
//			f.setInvestment(parseFinance(invset);
//			result.add(newF);
//		}
//		
//		return result;
//	}
//	
//	public String parseFinance(String finance){
//		
//		int len = finance.length();
//		String value = finance;
//		
//		if(finance.indexOf("m") > -1 || finance.indexOf("k")>-1 || finance.indexOf("b")>-1){
//			return finance;
//		}
//		
//		if(len > 9) 
//			 	value = value.substring(0, len-9)+'b';
//		else if(len > 6) 
//			 	value = value.substring(0, len-6)+'m';
//	    else if(len > 3) 
//	    		value = value.substring(0, len-3)+'k';
//		
//		
//		return value;
//	}

	
	
	public String parseDesc(String desc){
		if(desc != ""){
			if(desc.length() > 80) desc = desc.substring(0, 80)+"...";
		}
		
		return desc;
	}
	
	

	

	
}
