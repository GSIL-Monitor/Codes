package com.tsb.dao.read;

import java.util.List;

import com.tsb.model.Product;

public interface ProductReadDao {
	List<Product> get(Integer companyId);
}
