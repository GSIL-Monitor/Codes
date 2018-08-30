package com.tsb.company.dao;

import java.util.List;

import org.apache.ibatis.annotations.Param;

import com.tsb.company.vo.CompanyDescVO;
import com.tsb.company.vo.CompanySearchVO;
import com.tsb.company.vo.CompanyVO;
import com.tsb.company.vo.SourceVO;

@SuppressWarnings("rawtypes")
public interface CompanyVODao {
	CompanySearchVO getById(Integer id);

	List getSearch(@Param("companyIds") List companyIds);

	List getSearchByCodes(@Param("codes") List codes);

	CompanyVO getByCode(String code);

	CompanyDescVO getDesc(String code);

	String getName(String code);

	List<CompanySearchVO> getSortSearch(@Param("companyIds") List companyIds, @Param("sectorId") Integer sectorId,
			@Param("locationId") Integer locationId, @Param("round") Integer round);
	
	CompanySearchVO getSort(@Param("id") Integer id, @Param("sectorId") Integer sectorId,
			@Param("locationId") Integer locationId, @Param("round") Integer round);
	
	SourceVO getSource(Integer companyId);
}
