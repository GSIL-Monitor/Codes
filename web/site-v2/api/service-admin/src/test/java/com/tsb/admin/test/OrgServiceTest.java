package com.tsb.admin.test;

import java.util.List;

import org.junit.Assert;
import org.junit.Test;
import org.springframework.beans.factory.annotation.Autowired;

import com.tsb.admin.service.OrgService;

public class OrgServiceTest extends BaseTest {
	@Autowired
	private OrgService orgService;

	@SuppressWarnings("rawtypes")
	@Test
	public void getOrg() {
		List list = orgService.getOrgs();
		System.out.println(list.get(0));
		Assert.assertEquals("fail", "Gobi Partners", list.get(0));
	}

}
