# Create ENV
```
conda env create -f /path/to/environment.yml
```

# Create your own event
```
class MyEventStudy(esprocess.EventStudy):
    def __init__(self, df):
        # Call the parent class's __init__ method
        super().__init__(df)
        self.original_df = df

    def create_events(self):
        # Call the parent class's create_events method
        self.tick_event_dict[f'1101'] = ['2020-04-10']
        self.tick_event_dict[f'1102'] = ['2020-04-10']
```

# Params
- stock filter list (the tick you want to test)
- event window [T2, T3]
- estimation size [T0, T1]
- Buffer size [T1, T2]<br>
    used to estimate $\bar{CAR}(T1, T2)$ and $var(\bar{CAR}(T1, T2))$

![fig4](../1223/img/fig4.png)

- n_signal : the number of the frequency an event appear in a tick
- positive_sig_percent : how many CARs are significant in the post-event window
```
PARAMS = {
    
    'stock_filter_list':['1101', '1102'],
    'event_window':(0,+10),
    'estimation_size':30,
    'buffer_size':30,
    'window_size':10,
    'n_signal':10,
    'positive_sig_percent':0.8
}
```
