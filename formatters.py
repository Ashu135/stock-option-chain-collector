from typing import Dict, Any, List
import math

def get_middle_slice(data_list: List[Any], slice_size: int = 20) -> List[Any]:
    """Get a slice of data from the middle of the list"""
    if len(data_list) <= slice_size:
        return data_list
        
    start_idx = math.floor((len(data_list) - slice_size) / 2)
    end_idx = start_idx + slice_size
    return data_list[start_idx:end_idx]

def format_option_data(option_data: Dict[str, Any]) -> dict:
    """Format a single option chain entry with additional fields"""
    return {
        "Strike Price": option_data["strike_price"],
        "Expiry": option_data["expiry_date"],
        "PCR": option_data["pcr"],
        "Symbol": option_data["symbol_name"],
        "Index Close": option_data["index_close"],
        "Time": option_data["time"],
        "Calls": {
            "OI": option_data["calls_oi"],
            "Change in OI": option_data["calls_change_oi"],
            "Volume": option_data["calls_volume"],
            "IV": option_data["calls_iv"],
            "LTP": option_data["calls_ltp"],
            "Net Change": option_data["calls_net_change"],
            "Bid Price": option_data["calls_bid_price"],
            "Ask Price": option_data["calls_ask_price"],
            "Open": option_data["calls_open"],
            "High": option_data["calls_high"],
            "Low": option_data["calls_low"],
            "OI Value": option_data["calls_oi_value"],
            "Change OI Value": option_data["calls_change_oi_value"],
            "Average Price": option_data["calls_average_price"],
            "Buildup": option_data["calls_builtup"],
            "Intrinsic": option_data["calls_intrisic"],
            "Time Value": option_data["calls_time_value"],
            "Greeks": {
                "Delta": option_data["call_delta"],
                "Gamma": option_data["call_gamma"],
                "Theta": option_data["call_theta"],
                "Vega": option_data["call_vega"],
                "Rho": option_data["call_rho"]
            }
        },
        "Puts": {
            "OI": option_data["puts_oi"],
            "Change in OI": option_data["puts_change_oi"],
            "Volume": option_data["puts_volume"],
            "IV": option_data["puts_iv"],
            "LTP": option_data["puts_ltp"],
            "Net Change": option_data["puts_net_change"],
            "Bid Price": option_data["puts_bid_price"],
            "Ask Price": option_data["puts_ask_price"],
            "Open": option_data["puts_open"],
            "High": option_data["puts_high"],
            "Low": option_data["puts_low"],
            "OI Value": option_data["puts_oi_value"],
            "Change OI Value": option_data["puts_change_oi_value"],
            "Average Price": option_data["puts_average_price"],
            "Buildup": option_data["puts_builtup"],
            "Intrinsic": option_data["puts_intrisic"],
            "Time Value": option_data["puts_time_value"],
            "Greeks": {
                "Delta": option_data["put_delta"],
                "Gamma": option_data["put_gamma"],
                "Theta": option_data["put_theta"],
                "Vega": option_data["put_vega"],
                "Rho": option_data["put_rho"]
            }
        }
    }

def format_totals(totals_data: Dict[str, Any]) -> dict:
    """Format the totals information"""
    return {
        "ITM Calls": {
            "OI": totals_data["itm_total_calls"]["itm_total_calls_oi"],
            "Change in OI": totals_data["itm_total_calls"]["itm_total_calls_change_oi"],
            "Volume": totals_data["itm_total_calls"]["itm_total_calls_volume"]
        },
        "ITM Puts": {
            "OI": totals_data["itm_total_puts"]["itm_total_puts_oi"],
            "Change in OI": totals_data["itm_total_puts"]["itm_total_puts_change_oi"],
            "Volume": totals_data["itm_total_puts"]["itm_total_puts_volume"]
        },
        "OTM Calls": {
            "OI": totals_data["otm_total_calls"]["otm_total_calls_oi"],
            "Change in OI": totals_data["otm_total_calls"]["otm_total_calls_change_oi"]
        },
        "OTM Puts": {
            "OI": totals_data["otm_total_puts"]["otm_total_puts_oi"],
            "Change in OI": totals_data["otm_total_puts"]["otm_total_puts_change_oi"],
            "Volume": totals_data["otm_total_puts"]["otm_total_puts_volume"]
        },
        "Total": {
            "Calls OI": totals_data["total_calls_puts"]["total_calls_oi"],
            "Calls Change in OI": totals_data["total_calls_puts"]["total_calls_change_oi"],
            "Calls Volume": totals_data["total_calls_puts"]["total_calls_volume"],
            "Puts OI": totals_data["total_calls_puts"]["total_puts_oi"],
            "Puts Change in OI": totals_data["total_calls_puts"]["total_puts_change_oi"],
            "Puts Volume": totals_data["total_calls_puts"]["total_puts_volume"]
        }
    }