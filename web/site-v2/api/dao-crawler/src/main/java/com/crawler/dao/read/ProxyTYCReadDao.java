package com.crawler.dao.read;

import org.apache.ibatis.annotations.Param;

import com.crawler.model.ProxyTYC;

public interface ProxyTYCReadDao {
	ProxyTYC get(@Param("ip") String ip, @Param("port") int port, @Param("type") String type);
	int count();
}
