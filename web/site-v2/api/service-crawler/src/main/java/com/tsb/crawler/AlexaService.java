package com.tsb.crawler;

import java.util.Map;

@SuppressWarnings("rawtypes")
public interface AlexaService {

	Map findAlexa(String domain, int limit);
}
