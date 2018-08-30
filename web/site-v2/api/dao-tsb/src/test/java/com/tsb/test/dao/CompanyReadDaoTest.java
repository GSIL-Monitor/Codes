package com.tsb.test.dao;

import javax.annotation.Resource;

import org.junit.Assert;
import org.junit.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.transaction.annotation.Transactional;

import com.tsb.dao.read.company.CompanyReadDao;
import com.tsb.model.company.Company;
@Transactional
public class CompanyReadDaoTest extends BaseTest {
@Resource
private CompanyReadDao companyReadDao;
	
	@Test
	public void getByCodeTest(){
		String code = "Hetong-qshzhsh";
		Company company=companyReadDao.getByCode(code);
		System.out.println(company.getName());
		Assert.assertEquals("相等", "Hetong1 - 企业事务助手", company.getName());
	}

}
