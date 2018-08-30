package com.tsb.company.util;

import java.util.ArrayList;
import java.util.List;

import org.springframework.stereotype.Component;

import com.tsb.company.vo.CompanySearchVO;

@SuppressWarnings("rawtypes")
@Component
public class CompanyUtil {

	public List sortCompanies(List<CompanySearchVO> companies, List list){
		List result = new ArrayList<CompanySearchVO>();
		
		for(int i=0; i<list.size(); i++){
			for(CompanySearchVO vo: companies){
				if(vo.getCode().equals(list.get(i)) || vo.getId().equals(list.get(i))){
					result.add(vo);
				}
			}
		}
		
		return result;
	}
}
