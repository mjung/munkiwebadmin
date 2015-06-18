from django.contrib import admin

from django import forms

from manifests.models import Manifest
from catalogs.models import Catalog

# Register your models here.

from jssmanifests.models import JSSComputerAttributeType, JSSComputerAttributeMapping


import jssmanifests.utils as utils

class JSSComputerAttributeTypeAdmin(admin.ModelAdmin):

    fieldsets = [
        (None,               {'fields': ['label']}),
        ('Retrieval information', {'fields': ['computer_xpath',
                                              'api_path',
                                              'api_xpath',
                                              'xpath_needs_key' ] }),
    ]

    def get_actions(self, request):
        actions = super(JSSComputerAttributeTypeAdmin, self).get_actions(request)
        if request.user.is_superuser:
            return actions
   
        return None


class JSSComputerAttributeMappingAdminForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(JSSComputerAttributeMappingAdminForm, self).__init__(*args, **kwargs)
        self.fields['manifest_name'].widget = \
            forms.widgets.Select( choices=utils.get_manifest_selectlist())
        self.fields['catalog_name'].widget  = \
            forms.widgets.Select( choices=utils.get_catalog_selectlist())
        self.fields['package_name'].widget  = \
            forms.widgets.Select( choices=utils.get_packagename_selectlist())

    def clean_package_name(self):

        package_name = self.cleaned_data['package_name']
        package_name_list = utils.get_packagenamelist()

        if package_name and package_name_list.count(package_name) != 1:
            raise forms.ValidationError( "Package name %(pname)s is not in list of packages", params = { 'pname': package_name } ) 

        return package_name

    def clean_manifest_name(self):

        manifest_name = self.cleaned_data['manifest_name']
        manifest_list = utils.get_manifestlist()

        if manifest_name and manifest_list.count(manifest_name) != 1:
            raise forms.ValidationError( "Manifest name %(mname)s is not in list of manifests", params = { 'mname': manifest_name } ) 

        return manifest_name

    def clean_catalog_name(self):

        catalog_name = self.cleaned_data['catalog_name']
        catalog_list = utils.get_cataloglist()

        if catalog_name and catalog_list.count(catalog_name) != 1:
            raise forms.ValidationError( "Catalog name %(cname)s is not in list of catalogs", params = { 'cname': catalog_name } ) 

        return catalog_name


    def clean(self): 
      
        validation_errors = []

        cleaned_data = super(JSSComputerAttributeMappingAdminForm, self).clean()

        jss_computer_attribute_type = \
            cleaned_data.get('jss_computer_attribute_type')
        attribute_key =  cleaned_data.get('jss_computer_attribute_key')

        if jss_computer_attribute_type.xpath_needs_key and not attribute_key:
                validation_errors.append( forms.ValidationError( "Attribute type %(attribute_type)s requires a key for mapping", params = { 'attribute_type': jss_computer_attribute_type })  ) 

        if not jss_computer_attribute_type.xpath_needs_key and attribute_key:
                validation_errors.append( forms.ValidationError( "Attribute type %(attribute_type)s does not require a key for mapping", params = { 'attribute_type': jss_computer_attribute_type })  ) 

        # The following is long and ugly, but checks that the correct
        # set of fields is set for each mapping type
        manifest_element_type = cleaned_data.get('manifest_element_type')
        manifest_name         = cleaned_data.get('manifest_name')
        catalog_name          = cleaned_data.get('catalog_name')
        package_name          = cleaned_data.get('package_name')
        package_action        = cleaned_data.get('package_action')

        if manifest_element_type == 'c':
           if manifest_name:
                validation_errors.append( forms.ValidationError( "Catalog mappings should not have a manifest name set") ) 
 
           if not catalog_name:
                validation_errors.append( forms.ValidationError( "Catalog mappings should have a valid catalog name set") ) 

           if package_name:
               validation_errors.append( forms.ValidationError( "Catalog mappings should not have a package name set") ) 

           if package_action:
               validation_errors.append( forms.ValidationError( "Catalog mappings should not have a package action set") ) 

        if manifest_element_type == 'm':
           if not manifest_name:
                validation_errors.append( forms.ValidationError( "Manifest mappings should have a valid manifest name set") ) 
 
           if catalog_name:
                validation_errors.append( forms.ValidationError( "Manifest mappings should not have a catalog name set") ) 

           if package_name:
               validation_errors.append( forms.ValidationError( "Manifest mappings should not have a package name set") ) 

           if package_action:
               validation_errors.append( forms.ValidationError( "Manifest mappings should not have a package action set") ) 

        if manifest_element_type == 'p':
           if manifest_name:
                validation_errors.append( forms.ValidationError( "Package mappings should not have a manifest name set") ) 
 
           if catalog_name:
                validation_errors.append( forms.ValidationError( "Package mappings should not have a catalog name set") ) 

           print package_name
           if not package_name:
               validation_errors.append( forms.ValidationError( "Package mappings should have a valid package name set") ) 

           if not package_action:
               validation_errors.append( forms.ValidationError( "Package mappings should have a valid package action set") ) 

#        attribute_type = \
#            cleaned_data.get('jss_computer_attribute_type')

#        print self.instance
#
#        if xpath_needs_key \
#            and not cleaned_data.get('jss_computer_attribute_key'):
#            validation_errors.append( forms.ValidationError( "Mapping attribute type %(type)s needs a key, and there is not one set", params={'type': self.jss_computer_attribute_type.label} ) )
#
        # Look up relation and check xpath_needs_key
        # Check manifest given exists
#
        if len(validation_errors) > 0:
            raise forms.ValidationError(validation_errors)
       



class JSSComputerAttributeMappingAdmin(admin.ModelAdmin):

    form = JSSComputerAttributeMappingAdminForm

    fieldsets = [
        (None,               {'fields': [ 'jss_computer_attribute_key',
                                          'jss_computer_attribute_value',
                                          'jss_computer_attribute_type',
                                          'manifest_element_type',
                                          'remove_from_xml',
                                          'priorty',
                                          'site',
                                          'enabled',
            ]}),
        ('Catalog Settings', {'fields': [ 'catalog_name', ] } ),
        ('Manifest Settings', {'fields': ['manifest_name', ] } ),
        ('Package Settings', {'fields': ['package_name',
                                         'package_action'] }),
    ]

    list_display = ('__str__', 'enabled')

#   Bulk actions
#   Enable selected mappings
    def bulk_enable_attribute_mappings(self, request, queryset):
        self._bulk_enable_disable(request, queryset, True, 'enable')
    bulk_enable_attribute_mappings.short_description = "Enable selected mappings"
#   Disable selected mappings
    def bulk_disable_attribute_mappings(self, request, queryset):
        self._bulk_enable_disable(request, queryset, False, 'disable')

    bulk_disable_attribute_mappings.short_description = "Disable selected mappings"

    def _bulk_enable_disable(self, request, queryset, flag, action):
        rows_updated = queryset.update(enabled=flag)
        if rows_updated == 1:
            message_bit = "1 mapping was"
        else:
            message_bit = "%s mapping were" % rows_updated

        self.message_user(request, "%s successfully marked as %s." \
             % (message_bit, action) )


    actions = [ 'bulk_enable_attribute_mappings',
                'bulk_disable_attribute_mappings' ]

admin.site.register(JSSComputerAttributeType, JSSComputerAttributeTypeAdmin)
admin.site.register(JSSComputerAttributeMapping, JSSComputerAttributeMappingAdmin)
