package com.tsb.dao.read.company;

import java.util.List;

import com.tsb.model.company.Product;

public interface ProductReadDao {
	List<Product> get(Integer companyId);
}
