from odoo.tests import tagged
from odoo.tests.common import Form, TransactionCase
from odoo.exceptions import UserError


@tagged('post_install', '-at_install')
class EstateTestCase(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super(EstateTestCase, cls).setUpClass()

        cls.properties = cls.env['estate.property'].create([{
            'name': 'prop1',
            'expected_price': 10000,
        }])
        cls.buyer = cls.env['res.partner'].create({
            'name': 'buyer',
        })
        cls.offers = cls.env['estate.property.offer'].create([{
            'partner_id': cls.buyer.id,
            'property_id': cls.properties[0].id,
            'price': 9000,
        }])

    def test_offer_creation_on_sold(self):
        with self.assertRaises(UserError):
            self.properties.action_sell()

        self.offers.action_accept()
        self.properties.action_sell()
        self.assertRecordValues(self.properties, [
            {'state': 'sold'}
        ])

        with self.assertRaises(UserError):
            self.env['estate.property.offer'].create([{
                'partner_id': self.buyer.id,
                'property_id': self.properties[0].id,
                'price': 9000,
            }])

    def test_property_form(self):
        with Form(self.properties[0]) as prop:
            self.assertEqual(prop.garden_area, 0)
            self.assertIs(prop.garden_orientation, False)

            prop.garden = True
            self.assertEqual(prop.garden_area, 10)
            self.assertEqual(prop.garden_orientation, "N")

            prop.garden = False
            self.assertEqual(prop.garden_area, 0)
            self.assertIs(prop.garden_orientation, False)
