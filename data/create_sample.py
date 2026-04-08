import pandas as pd                                                                                                                                                       
                  
daily = pd.read_parquet("daily_data_in_sample.parquet")
sample = daily[daily["trade_day_id"].isin(daily["trade_day_id"].unique()[:20])]
sample.to_parquet("daily_sample.parquet")                                                                                                                                 
                                                                                                                                                                            
lob = pd.read_parquet("lob_data_in_sample.parquet",                                                                                                                       
                        filters=[("trade_day_id", "in", ["D001","D002","D003"])])                                                                                           
lob.to_parquet("lob_sample.parquet")   