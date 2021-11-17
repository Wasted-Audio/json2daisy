import jinja2
import json
import os
import pkg_resources

json_defaults_file = ''

# helper for loading and processing the defaults, component list, etc
def map_load(pair):
	# load the default components
	comp_string = pkg_resources.resource_string(__name__, json_defaults_file)
	component_defaults = json.loads(comp_string)

	pair[1]['name'] = pair[0]

	# the default if it exists
	component = component_defaults[pair[1]['component']]
	if(component):
		# copy component defaults into the def
		# TODO this should be recursive for object structures..
		for k in component:
			if not k in pair[1]: 
				pair[1][k] = component[k]
	else:
		raise Exception("undefined component kind: ", pair[1]['component'])

	return pair[1]

def filter_match(set, key, match, key_exclude=None, match_exclude=None):
	if (key_exclude is not None and match_exclude is not None):
		return filter(lambda x: x.get(key, '') == match and x.get(key_exclude, '') != match_exclude, set)
	else:
		return filter(lambda x: x.get(key, '') == match, set)

def filter_matches(set, key, matches, key_exclude=None, match_exclude=None):
	if (key_exclude is not None and match_exclude is not None):
		return filter(lambda x: x.get(key, '') in matches and x.get(key_exclude, '') != match_exclude, set)
	else:
		return filter(lambda x: x.get(key, '') in matches, set)

def filter_has(set, key, key_exclude=None, match_exclude=None):
	if (key_exclude is not None and match_exclude is not None):
		return filter(lambda x: x.get(key, '') != '' and x.get(key_exclude, '') != match_exclude, set)
	else:
		return filter(lambda x: x.get(key, '') != '', set)

# filter out the components we need, then map them onto the init for that part
def filter_map_init(set, key, match, key_exclude=None, match_exclude=None):
	filtered = filter_match(set, key, match, key_exclude=key_exclude, match_exclude=match_exclude)
	return "\n    ".join(map(lambda x: x['map_init'].format_map(x), filtered)) 

def filter_map_set(set, key, match, key_exclude=None, match_exclude=None):
	filtered = filter_match(set, key, match, key_exclude=key_exclude, match_exclude=match_exclude)
	return "\n    ".join(map(lambda x: x['mapping'][0]['set'].format_map(x['mapping'][0]['name'].format_map(x)), filtered))

def filter_map_ctrl(set, key, matches, init_key, key_exclude=None, match_exclude=None):
	set = filter_matches(set, key, matches, key_exclude=key_exclude, match_exclude=match_exclude)
	set = map(lambda x, i: {**x, 'i': i}, set, range(1000))
	return "\n    ".join(map(lambda x: x[init_key].format_map(x), set))

# filter out the components with a certain field, then fill in the template
def filter_map_template(set, name, key_exclude=None, match_exclude=None):
	filtered = filter_has(set, name, key_exclude=key_exclude, match_exclude=match_exclude)
	return "\n    ".join(map(lambda x: x[name].format_map(x), filtered))

def flatten_pin_dicts(comp):
	newcomp = {}
	for key,val in comp.items():
		if (isinstance(val, dict) and key == 'pin'):
			for subkey, subval in val.items():
				newcomp[key + '_' + subkey] = subval
		else:
			newcomp[key] = val

	return newcomp

def flatten_index_dicts(comp):
	newcomp = {}
	for key,val in comp.items():
		if (isinstance(val, dict) and key == 'index'):
			for subkey, subval in val.items():
				newcomp[key + '_' + subkey] = subval
		else:
			newcomp[key] = val

	return newcomp

def bools_to_lower_str(comp):
	new_comp = {}
	for key, val in comp.items():
		new_comp[key] = str(val).lower() if isinstance(val, bool) else val

	return new_comp

def get_output_array(components):
	output_comps = len(list(filter_match(components, 'direction', 'out')))
	return 'float output_data[{output_comps}];'

def generate_header(board_description_file):

  # if board_description_file != '':
  #   try:
  #     with open(board_description_file, 'rb') as file:
  #       target = json.load(file)
  #   except FileNotFoundError:
  #     raise FileNotFoundError(f'Could not find board description file "{board_description_file}"')
  # else:
  #   try:
  #     default_description = pkg_resources.resource_string(__name__, os.path.join('resources', f'{board_name}.json'))
  #     target = json.loads(default_description)
  #   except FileNotFoundError:
  #     raise FileNotFoundError(f'Unknown Daisy board "{board_name}"')
  with open(board_description_file, 'rb') as file:
    target = json.load(file)
  
  # flesh out target components:
  components = target['components']
  parents = target.get('parents', {})

  for key in parents:
    parents[key]['is_parent'] = True
  components.update(parents)

  seed_defaults = os.path.join("resources", 'component_defaults.json')
  patchsm_defaults = os.path.join("resources", 'component_defaults_patchsm.json')
  defaults = {'seed': seed_defaults, 'patch_sm': patchsm_defaults}
  som = target.get('som', 'seed')

  global json_defaults_file
  try:
    json_defaults_file = defaults[som]
  except KeyError:
    raise NameError(f'Unkown som "{som}"')

  # alphabetize by component name
  components = sorted(components.items(), key=lambda x: x[1]['component'])
  components = list(map(map_load, components))

  # flatten pin dicts into multiple entries
  # e.g. "pin": {"a": 12} => "pin_a": 12
  components = [flatten_pin_dicts(comp) for comp in components]
  components = [flatten_index_dicts(comp) for comp in components]

  """
  This corrupts booleans that might be used for python parsing, and
  so should be avoided. If the user wants to insert C parameters, they
  should just be strings
  """
  # # convert booleans to properly cased strings
  # components = [bools_to_lower_str(comp) for comp in components]

  target['components'] = components
  if not 'name' in target:
    target['name'] = 'custom'

  if not 'aliases' in target:
    target['aliases'] = {}

  if 'display' in target:
    # apply defaults
    target['display'] = {
      'driver': "daisy::SSD130x4WireSpi128x64Driver",
      'config': [],
      'dim': [128, 64]
    }
    
    target['defines']['OOPSY_TARGET_HAS_OLED'] = 1
    target['defines']['OOPSY_OLED_DISPLAY_WIDTH'] = target['display']['dim'][0]
    target['defines']['OOPSY_OLED_DISPLAY_HEIGHT'] = target['display']['dim'][1]

  replacements = {}
  replacements['name'] = target['name']
  replacements['som'] = som
  replacements['external_codecs'] = target.get('external_codecs', [])
  replacements['som_class'] = 'daisy::DaisySeed' if som == 'seed' else 'daisy::patch_sm::DaisyPatchSM'

  # replacements['linker_script'] = meta['daisy'].get('linker_script', '')
  # if replacements['linker_script'] != '':
  #   replacements['linker_script'] = f'../{meta["daisy"]["linker_script"]}'

  # depth = meta['daisy'].get('libdaisy_depth', 3)
  # replacements['libdaisy_path'] = f'{"../" * depth}libdaisy'

  # replacements['class_name'] = class_name

  replacements['display_conditional'] = ('#include "dev/oled_ssd130x.h"' if ('display' in target) else  "")
  replacements['target_name'] = target['name']
  replacements['init'] = filter_map_template(components, 'init', key_exclude='default', match_exclude=True)

  replacements['cd4021'] = filter_map_init(components, 'component', 'CD4021', key_exclude='default', match_exclude=True)
  replacements['i2c'] = filter_map_init(components, 'component', 'i2c', key_exclude='default', match_exclude=True)
  replacements['pca9685'] = filter_map_init(components, 'component', 'PCA9685', key_exclude='default', match_exclude=True)
  replacements['switch'] = filter_map_init(components, 'component', 'Switch', key_exclude='default', match_exclude=True)
  replacements['gatein'] = filter_map_init(components, 'component', 'GateIn', key_exclude='default', match_exclude=True)
  replacements['encoder'] = filter_map_init(components, 'component', 'Encoder', key_exclude='default', match_exclude=True)
  replacements['switch3'] = filter_map_init(components, 'component', 'Switch3', key_exclude='default', match_exclude=True)
  replacements['analogcount'] = len(list(filter_matches(components, 'component', ['AnalogControl', 'AnalogControlBipolar', 'CD4051'], key_exclude='default', match_exclude=True)))

  replacements['init_single'] = filter_map_ctrl(components, 'component', ['AnalogControl', 'AnalogControlBipolar', 'CD4051'], 'init_single', key_exclude='default', match_exclude=True)
  replacements['ctrl_init'] = filter_map_ctrl(components, 'component', ['AnalogControl', 'AnalogControlBipolar'], 'map_init', key_exclude='default', match_exclude=True)	

  replacements['ctrl_mux_init'] = filter_map_init(components, 'component', 'CD4051AnalogControl', key_exclude='default', match_exclude=True)

  replacements['led'] = filter_map_init(components, 'component', 'Led', key_exclude='default', match_exclude=True)
  replacements['rgbled'] = filter_map_init(components, 'component', 'RgbLed', key_exclude='default', match_exclude=True)
  replacements['gateout'] = filter_map_init(components, 'component', 'GateOut', key_exclude='default', match_exclude=True)
  replacements['dachandle'] = filter_map_init(components, 'component', 'CVOuts', key_exclude='default', match_exclude=True)

  # replacements['callback_write_out'] = filter_map_set(components, 'direction', 'out')
  
  replacements['display'] = '// no display' if not 'display' in target else \
    'daisy::OledDisplay<' + target['display']['driver'] + '>::Config display_config;\n    ' +\
    'display_config.driver_config.transport_config.Defaults();\n    ' +\
    "".join(map(lambda x: x, target['display'].get('config', {}))) +\
    'display.Init(display_config);\n'

  replacements['process'] = filter_map_template(components, 'process', key_exclude='default', match_exclude=True)
  # There's also this after {process}. I don't see any meta in the defaults json at this time. Is this needed?
  # ${components.filter((e) => e.meta).map((e) => e.meta.map(m=>`${template(m, e)}`).join("")).join("")}

  replacements['postprocess'] = filter_map_template(components, 'postprocess', key_exclude='default', match_exclude=True)
  replacements['displayprocess'] = filter_map_template(components, 'display', key_exclude='default', match_exclude=True)
  replacements['hidupdaterates'] = filter_map_template(components, 'updaterate', key_exclude='default', match_exclude=True)

  component_declarations = list(filter(lambda x: not x.get('default', False), components))
  component_declarations = list(filter(lambda x: x.get('typename', '') != '', component_declarations))
  if len(component_declarations) > 0:
    replacements['comps'] = ";\n  ".join(map(lambda x: x['typename'].format_map(x) + ' ' + x['name'], component_declarations)) + ';'
  non_class_declarations = list(filter(lambda x: 'non_class_decl' in x, component_declarations))
  if len(non_class_declarations) > 0:
    replacements['non_class_declarations'] = "\n  ".join(map(lambda x: x['non_class_decl'].format_map(x), non_class_declarations))

  replacements['dispdec'] = ('daisy::OledDisplay<' + target['display']['driver'] + '> display;') if ('display' in target) else  "// no display"

  replacements['output_arrays'] = get_output_array(components)

  replacements['parameters'] = []
  replacements['output_parameters'] = []
  replacements['callback_write_out'] = ''
  replacements['loop_write_out'] = ''
  replacements['callback_write_in'] = []
  
  env_opts = {"trim_blocks": True, "lstrip_blocks": True}

  # Ideally, this would be what we use, but we'll need to get the jinja PackageLoader class working
  # loader = jinja2.PackageLoader(__name__)
  # env = jinja2.Environment(loader=loader, **env_opts)
  # rendered_header = env.get_template('daisy.h').render(replacements)

  # This following works, but is really annoying
  header_str = pkg_resources.resource_string(__name__, os.path.join('templates', 'daisy.h'))
  header_env = jinja2.Environment(loader=jinja2.BaseLoader(), **env_opts).from_string(header_str.decode('utf-8'))

  rendered_header = header_env.render(replacements)
  
  # removing all unnecessary fields
  for comp in components:
    del comp['map_init']
    del comp['typename']

  return rendered_header, target['name'], components

if __name__ == '__main__':
  import argparse

  parser = argparse.ArgumentParser(description='Convert JSON board descriptions to C++ headers.')
  parser.add_argument('infile', type=str,
                      help='input JSON file')
  parser.add_argument('-o', type=str, default=None,
                      help='output file name')
  
  args = parser.parse_args()
  header, name, components = generate_header(args.infile)
  outfile = args.o if args.o is not None else f'j2daisy_{name}.h'
  with open(outfile, 'w') as file:
    file.write(header)
  
  print(f'Generated Daisy C++ header in "{outfile}"')