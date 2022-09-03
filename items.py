#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@Project ：fastApiYFQSY 
@File    ：items.py
@Author  ：yszar
@Date    ：2022/9/3 12:08 
"""
from pydantic import BaseModel


class Session(BaseModel):
    code: str
